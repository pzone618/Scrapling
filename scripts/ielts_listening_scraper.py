"""
IELTS 听力测试爬虫 - 支持音频下载
输出目录: output/ielts_tests/
"""
from scrapling.fetchers import StealthyFetcher
import json
from pathlib import Path
from datetime import datetime
import urllib.request
from urllib.parse import urljoin, urlparse
import re

# 配置路径
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "ielts_tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_audio(url, output_path, test_name):
    """
    下载音频文件
    
    Args:
        url: 音频文件 URL
        output_path: 输出目录路径
        test_name: 测试名称（用于文件命名）
    
    Returns:
        str: 下载的文件路径，失败则返回 None
    """
    try:
        # 从 URL 获取文件扩展名
        parsed_url = urlparse(url)
        ext = Path(parsed_url.path).suffix or '.mp3'
        
        # 生成文件名
        audio_filename = f"{test_name}_audio{ext}"
        audio_path = output_path / audio_filename
        
        print(f"  正在下载音频: {url}")
        print(f"  保存到: {audio_path.relative_to(Path.cwd())}")
        
        # 下载文件
        urllib.request.urlretrieve(url, audio_path)
        
        file_size = audio_path.stat().st_size / (1024 * 1024)  # MB
        print(f"  ✓ 下载完成 ({file_size:.2f} MB)\n")
        
        return str(audio_path.relative_to(Path.cwd()))
        
    except Exception as e:
        print(f"  ✗ 下载失败: {e}\n")
        return None

def scrape_ielts_listening_test(url, output_name=None):
    """
    爬取 IELTS 听力测试（包括音频）
    
    Args:
        url: IELTS 测试页面 URL
        output_name: 输出文件名（不含扩展名），默认自动生成
    
    Returns:
        dict: 爬取的数据
    """
    print(f"正在爬取 IELTS 听力测试: {url}\n")
    
    # 使用 StealthyFetcher 获取页面
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True, wait=2)
    
    # 提取标题
    title = page.css('h1::text').get() or page.css('title::text').get() or "IELTS Listening Test"
    print(f"📖 标题: {title}\n")
    
    # 生成输出名称
    if output_name is None:
        output_name = title.lower().replace(' ', '_').replace('-', '_')
        output_name = ''.join(c for c in output_name if c.isalnum() or c == '_')
    
    # 提取音频链接
    audio_urls = []
    audio_files = []
    
    # 查找 <audio> 标签
    for audio in page.css('audio'):
        src = audio.attrib.get('src', '')
        if src:
            full_url = urljoin(url, src)
            audio_urls.append(full_url)
        
        # 查找 <source> 子标签
        for source in audio.css('source'):
            src = source.attrib.get('src', '')
            if src:
                full_url = urljoin(url, src)
                audio_urls.append(full_url)
    
    # 查找其他可能的音频链接 (mp3, wav, ogg)
    for link in page.css('a'):
        href = link.attrib.get('href', '')
        if re.search(r'\.(mp3|wav|ogg|m4a)(\?.*)?$', href, re.I):
            full_url = urljoin(url, href)
            audio_urls.append(full_url)
    
    # 去重
    audio_urls = list(set(audio_urls))
    
    if audio_urls:
        print(f"🎵 找到 {len(audio_urls)} 个音频文件\n")
        
        # 下载音频文件
        for i, audio_url in enumerate(audio_urls, 1):
            suffix = f"_{i}" if len(audio_urls) > 1 else ""
            downloaded_path = download_audio(audio_url, OUTPUT_DIR, f"{output_name}{suffix}")
            if downloaded_path:
                audio_files.append({
                    "url": audio_url,
                    "local_path": downloaded_path,
                    "index": i
                })
    else:
        print("⚠️  未找到音频文件\n")
    
    # 提取所有段落文本
    paragraphs = []
    for p in page.css('p::text').getall():
        text = p.strip()
        if text and len(text) > 20:
            paragraphs.append(text)
    
    # 提取所有标题
    headings = []
    for h in page.css('h2::text, h3::text, h4::text').getall():
        text = h.strip()
        if text:
            headings.append(text)
    
    # 提取列表项（可能包含问题）
    questions = []
    for li in page.css('li::text').getall():
        text = li.strip()
        if text and len(text) > 10:
            questions.append(text)
    
    # 提取链接
    links = []
    for a in page.css('a'):
        href = a.attrib.get('href', '')
        text = a.css('::text').get('').strip()
        if href and text and not re.search(r'\.(mp3|wav|ogg|m4a)(\?.*)?$', href, re.I):
            links.append({"text": text, "href": href})
    
    print(f"✓ 提取了 {len(paragraphs)} 段文本")
    print(f"✓ 提取了 {len(headings)} 个标题")
    print(f"✓ 提取了 {len(questions)} 个问题/列表项")
    print(f"✓ 提取了 {len(links)} 个链接")
    print(f"✓ 下载了 {len(audio_files)} 个音频文件\n")
    
    # 组织数据
    data = {
        "metadata": {
            "url": url,
            "title": title,
            "type": "listening_test",
            "scraped_at": datetime.now().isoformat(),
            "scraper_version": "2.0"
        },
        "audio": {
            "files": audio_files,
            "count": len(audio_files)
        },
        "content": {
            "headings": headings,
            "paragraphs": paragraphs,
            "questions": questions,
            "links": links[:20]
        },
        "stats": {
            "headings": len(headings),
            "paragraphs": len(paragraphs),
            "questions": len(questions),
            "links": len(links),
            "audio_files": len(audio_files)
        }
    }
    
    return data, output_name

def save_data(data, output_name):
    """保存数据为多种格式"""
    saved_files = {}
    
    # 保存 JSON
    json_file = OUTPUT_DIR / f"{output_name}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    saved_files['json'] = json_file
    print(f"💾 已保存: {json_file.relative_to(Path.cwd())}")
    
    # 保存 Markdown
    md_file = OUTPUT_DIR / f"{output_name}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# {data['metadata']['title']}\n\n")
        f.write(f"**来源:** {data['metadata']['url']}  \n")
        f.write(f"**类型:** {data['metadata']['type']}  \n")
        f.write(f"**爬取时间:** {data['metadata']['scraped_at']}  \n\n")
        f.write("---\n\n")
        
        # 音频文件信息
        if data['audio']['files']:
            f.write("## 🎵 音频文件\n\n")
            for audio in data['audio']['files']:
                f.write(f"- **音频 {audio['index']}**\n")
                f.write(f"  - 在线地址: {audio['url']}\n")
                f.write(f"  - 本地路径: `{audio['local_path']}`\n\n")
            f.write("---\n\n")
        
        # 目录结构
        if data['content']['headings']:
            f.write("## 📑 目录结构\n\n")
            for h in data['content']['headings']:
                f.write(f"- {h}\n")
            f.write("\n---\n\n")
        
        # 内容
        f.write("## 📝 内容\n\n")
        for para in data['content']['paragraphs']:
            f.write(f"{para}\n\n")
        
        # 问题
        if data['content']['questions']:
            f.write("\n## ❓ 问题/列表\n\n")
            for i, q in enumerate(data['content']['questions'], 1):
                f.write(f"{i}. {q}\n")
    
    saved_files['markdown'] = md_file
    print(f"💾 已保存: {md_file.relative_to(Path.cwd())}")
    
    # 保存纯文本
    txt_file = OUTPUT_DIR / f"{output_name}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"{data['metadata']['title']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"来源: {data['metadata']['url']}\n")
        f.write(f"类型: {data['metadata']['type']}\n")
        f.write(f"爬取时间: {data['metadata']['scraped_at']}\n\n")
        
        if data['audio']['files']:
            f.write("音频文件:\n")
            for audio in data['audio']['files']:
                f.write(f"  {audio['index']}. {audio['local_path']}\n")
            f.write("\n")
        
        f.write("=" * 60 + "\n\n")
        f.write("\n\n".join(data['content']['paragraphs']))
    
    saved_files['text'] = txt_file
    print(f"💾 已保存: {txt_file.relative_to(Path.cwd())}\n")
    
    return saved_files

def preview_data(data):
    """显示数据预览"""
    print("=" * 60)
    print("数据预览")
    print("=" * 60)
    
    print(f"\n📊 统计:")
    print(f"  - 音频文件: {data['stats']['audio_files']}")
    print(f"  - 标题数: {data['stats']['headings']}")
    print(f"  - 段落数: {data['stats']['paragraphs']}")
    print(f"  - 问题数: {data['stats']['questions']}")
    print(f"  - 链接数: {data['stats']['links']}")
    
    if data['audio']['files']:
        print(f"\n🎵 音频文件:")
        for audio in data['audio']['files']:
            print(f"  {audio['index']}. {audio['local_path']}")
    
    if data['content']['headings']:
        print(f"\n📑 前5个标题:")
        for i, h in enumerate(data['content']['headings'][:5], 1):
            print(f"  {i}. {h}")
    
    if data['content']['paragraphs']:
        print(f"\n📝 第一段内容:")
        preview = data['content']['paragraphs'][0][:200]
        print(f"  {preview}..." if len(data['content']['paragraphs'][0]) > 200 else f"  {preview}")

def main():
    """主函数"""
    # IELTS 听力测试 URL
    url = 'https://engnovate.com/ielts-listening-tests/cambridge-ielts-20-academic-listening-test-4/'
    
    # 也可以爬取阅读测试
    # url = 'https://engnovate.com/ielts-reading-tests/cambridge-ielts-20-academic-reading-test-4/'
    
    try:
        # 爬取数据
        data, output_name = scrape_ielts_listening_test(url)
        
        # 保存数据
        saved_files = save_data(data, output_name)
        
        # 显示预览
        preview_data(data)
        
        print(f"\n✅ 完成! 文件保存在 {OUTPUT_DIR.relative_to(Path.cwd())}/ 目录")
        
        return saved_files
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    main()
