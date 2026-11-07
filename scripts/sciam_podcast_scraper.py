"""
Scientific American「Science Quickly」播客爬虫
输出目录: output/sciam/

功能:
  - 抓取单期节目，或翻页批量抓取节目列表
  - 提取元数据(JSON-LD)、完整文字稿、音频地址
  - 每期保存为 Markdown + JSON，另生成汇总 index.json
  - 可选下载 mp3（--mp3）
  - 已抓取的期数自动跳过（--force 强制重抓），支持断点续抓

用法:
  # 单期
  uv run python scripts/sciam_podcast_scraper.py --url https://www.scientificamerican.com/podcast/episode/are-ai-chatbots-making-us-less-human/

  # 批量: 抓列表前 2 页（每页约 12 期），并下载 mp3
  uv run python scripts/sciam_podcast_scraper.py --pages 2 --mp3

  # 最多抓 5 期
  uv run python scripts/sciam_podcast_scraper.py --pages 3 --limit 5
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from scrapling.fetchers import FetcherSession

BASE_URL = "https://www.scientificamerican.com"
SHOW_URL = f"{BASE_URL}/podcast/science-quickly/"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "sciam"

AUDIO_RE = re.compile(r"https://[^\"'\s<>]*megaphone\.fm/[^\"'\s<>]+?\.mp3")
SPEAKER_RE = re.compile(r"[A-Z][\w.'’ -]{1,40}:")
# 允许 mp3 重定向到的域名（megaphone 及常见播客统计/CDN 跳转）
AUDIO_HOSTS = ("megaphone.fm", "podtrac.com", "pdst.fm", "chtbl.com", "pscrb.fm", "scientificamerican.com")
AD_PREFIXES =("If you're enjoying this article", "If you’re enjoying this article")


# ----------------------------------------------------------------------------
# 列表页
# ----------------------------------------------------------------------------
def collect_episode_urls(session: FetcherSession, pages: int, delay: float) -> list[str]:
    """翻页收集节目链接（保持页面顺序，去重）。"""
    urls: list[str] = []
    for page_no in range(1, pages + 1):
        list_url = SHOW_URL if page_no == 1 else f"{SHOW_URL}?page={page_no}"
        page = session.get(list_url)
        if page.status != 200:
            print(f"⚠️  列表页 {page_no} 返回 {page.status}，停止翻页")
            break

        found = [
            urljoin(BASE_URL, href.split("?")[0])
            for href in page.css('a[href*="/podcast/episode/"]::attr(href)').getall()
        ]
        new = [u for u in dict.fromkeys(found) if u not in urls]
        print(f"📄 列表页 {page_no}: 新增 {len(new)} 期")
        if not new:
            break
        urls.extend(new)

        if not page.css('a[href*="page="]'):  # 没有分页按钮 → 最后一页
            break
        time.sleep(delay)
    return urls


# ----------------------------------------------------------------------------
# 单期解析
# ----------------------------------------------------------------------------
def _json_ld(page) -> dict:
    for raw in page.css('script[type="application/ld+json"]::text').getall():
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for item in data if isinstance(data, list) else [data]:
            if item.get("@type") in ("NewsArticle", "Article", "PodcastEpisode"):
                return item
    return {}


def _transcript(page) -> list[str]:
    """提取正文段落：合并行内标签、过滤订阅广告、把“说话人:”并入下一段。"""
    bodies = page.css('div[class*="article__body"]')
    if not bodies:
        return []

    paras = []
    for p in bodies[0].css("p"):
        text = re.sub(r"\s+", " ", p.get_all_text(separator="", strip=False)).strip()
        if text and not text.startswith(AD_PREFIXES):
            paras.append(text)

    merged: list[str] = []
    for text in paras:
        if merged and SPEAKER_RE.fullmatch(merged[-1]):
            merged[-1] = f"{merged[-1]} {text}"
        else:
            merged.append(text)
    return merged


def parse_episode(page, url: str) -> dict:
    ld = _json_ld(page)
    authors = ld.get("author") or []
    if isinstance(authors, dict):
        authors = [authors]
    audio = AUDIO_RE.search(page.body.decode("utf-8", "ignore"))

    return {
        "slug": urlparse(url).path.rstrip("/").rsplit("/", 1)[-1],
        "url": ld.get("url") or url,
        "headline": ld.get("headline") or page.css("title::text").get("").split(" | ")[0],
        "alternativeHeadline": ld.get("alternativeHeadline"),
        "description": ld.get("description"),
        "datePublished": ld.get("datePublished"),
        "authors": [a.get("name") for a in authors if isinstance(a, dict)],
        "image": ld.get("thumbnailUrl"),
        "audio": audio.group(0) if audio else None,
        "isAccessibleForFree": ld.get("isAccessibleForFree"),
        "transcript": _transcript(page),
    }


def to_markdown(ep: dict) -> str:
    lines = [f"# {ep['headline']}"]
    if ep["alternativeHeadline"] or ep["description"]:
        lines.append(f"*{ep['alternativeHeadline'] or ''}* — {ep['description'] or ''}")
    lines += [
        "",
        "- 节目: Science Quickly (Scientific American)",
        f"- 发布: {(ep['datePublished'] or '')[:10]}",
        f"- 制作: {', '.join(ep['authors'])}",
        f"- 音频: {ep['audio'] or '无'}",
        f"- 原文: {ep['url']}",
        "",
        "---",
        "",
    ]
    for para in ep["transcript"]:
        speaker = SPEAKER_RE.match(para)
        if speaker:  # 说话人加粗
            para = f"**{speaker.group(0)}**{para[speaker.end():]}"
        lines.append(para + "\n")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# 下载 / 保存
# ----------------------------------------------------------------------------
def _get_audio(session: FetcherSession, url: str, max_hops: int = 10):
    """手动跟随音频重定向。

    Scrapling 默认的 follow_redirects="safe" 会拒绝解析到内网 IP 的跳转（SSRF 保护）。
    在 Clash/Surge 等 fake-IP / TUN 代理环境下，公网域名会被解析成 198.18.x.x 或 127.0.0.1，
    导致 megaphone 的 mp3 跳转被误拦。这里不整体关闭保护，而是逐跳检查域名白名单。
    """
    for _ in range(max_hops):
        host = urlparse(url).hostname or ""
        if not any(host == d or host.endswith("." + d) for d in AUDIO_HOSTS):
            print(f"   ⚠️  拒绝跳转到非白名单域名: {host}")
            return None
        resp = session.get(url, timeout=180, stealthy_headers=False, follow_redirects=False)
        location = resp.headers.get("location") or resp.headers.get("Location")
        if resp.status in (301, 302, 303, 307, 308) and location:
            url = urljoin(url, location)
            continue
        return resp
    print("   ⚠️  重定向次数过多")
    return None


def download_mp3(session: FetcherSession, ep: dict, out: Path) -> Path | None:
    if not ep["audio"]:
        print("   ⚠️  未找到音频地址")
        return None
    target = out / f"{ep['slug']}.mp3"
    if target.exists() and target.stat().st_size > 0:
        print("   🎧 mp3 已存在，跳过")
        return target

    resp = _get_audio(session, ep["audio"])
    if resp is None:
        return None
    if resp.status != 200 or not resp.body:
        print(f"   ⚠️  mp3 下载失败: HTTP {resp.status}")
        return None
    tmp = target.with_suffix(".mp3.part")
    tmp.write_bytes(resp.body)
    tmp.replace(target)
    print(f"   🎧 mp3 已保存 ({len(resp.body) / 1_048_576:.1f} MB)")
    return target


def scrape_episode(session: FetcherSession, url: str, out: Path, mp3: bool, force: bool) -> dict | None:
    slug = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
    json_path = out / f"{slug}.json"

    if json_path.exists() and not force:
        ep = json.loads(json_path.read_text(encoding="utf-8"))
        print(f"⏭️  已存在: {ep['headline']}")
    else:
        page = session.get(url)
        if page.status != 200:
            print(f"❌ {url} → HTTP {page.status}")
            return None
        ep = parse_episode(page, url)
        if not ep["transcript"]:
            print(f"⚠️  {slug}: 未提取到文字稿（页面结构可能已变化）")
        json_path.write_text(json.dumps(ep, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / f"{slug}.md").write_text(to_markdown(ep), encoding="utf-8")
        words = sum(len(p.split()) for p in ep["transcript"])
        print(f"✅ {ep['headline']}  ({len(ep['transcript'])} 段 / {words} 词)")

    if mp3:
        path = download_mp3(session, ep, out)
        ep["audio_file"] = path.name if path else None
    return ep


def write_index(out: Path) -> None:
    """根据目录里所有 JSON 重新生成汇总索引（按发布日期倒序）。"""
    items = []
    for f in out.glob("*.json"):
        if f.name == "index.json" or f.name.startswith("._"):
            continue
        try:
            ep = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        slug = ep.get("slug") or f.stem
        mp3 = out / f"{slug}.mp3"
        items.append({
            "slug": slug,
            **{k: ep.get(k) for k in ("headline", "datePublished", "url", "audio")},
            "words": sum(len(p.split()) for p in ep.get("transcript", [])),
            "mp3": mp3.name if mp3.exists() else None,
        })
    items.sort(key=lambda x: x["datePublished"] or "", reverse=True)
    (out / "index.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📚 索引已更新: {out / 'index.json'}（共 {len(items)} 期）")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Scientific American Science Quickly 播客爬虫")
    ap.add_argument("--url", action="append", help="单期节目 URL，可重复传入多个")
    ap.add_argument("--pages", type=int, default=1, help="批量模式：抓取的列表页数（默认 1，每页约 12 期）")
    ap.add_argument("--limit", type=int, default=0, help="最多抓取的期数（0 表示不限）")
    ap.add_argument("--mp3", action="store_true", help="同时下载 mp3 音频")
    ap.add_argument("--force", action="store_true", help="忽略已存在文件，强制重新抓取")
    ap.add_argument("--delay", type=float, default=1.5, help="请求间隔秒数（默认 1.5，请保持礼貌）")
    ap.add_argument("--out", type=Path, default=OUTPUT_DIR, help=f"输出目录（默认 {OUTPUT_DIR}）")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    with FetcherSession(impersonate="chrome", stealthy_headers=True, timeout=30, retries=3) as session:
        urls = args.url or collect_episode_urls(session, args.pages, args.delay)
        if args.limit:
            urls = urls[: args.limit]
        print(f"\n🎙️  共 {len(urls)} 期待处理 → {args.out}\n")

        ok = 0
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] ", end="")
            try:
                if scrape_episode(session, url, args.out, args.mp3, args.force):
                    ok += 1
            except Exception as e:  # 单期失败不影响整体
                print(f"❌ {url}: {e}")
            if i < len(urls):
                time.sleep(args.delay)

    write_index(args.out)
    print(f"🏁 完成: 成功 {ok}/{len(urls)}")


if __name__ == "__main__":
    main()
