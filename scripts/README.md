# Scripts 目录

此目录包含各种实用脚本和工具。

## IELTS 爬虫

### 📁 ielts_scraper.py

爬取 IELTS **阅读**测试页面的工具脚本。

**功能:**
- 爬取 IELTS 阅读测试页面内容
- 提取标题、段落、问题、链接
- 自动保存为 JSON、Markdown、TXT 三种格式
- 规范化输出路径到 `output/ielts_tests/` 目录

**使用方法:**

```bash
# 使用 uv 运行（推荐）
uv run python scripts/ielts_scraper.py

# 使用 python 运行
python scripts/ielts_scraper.py
```

### 📁 ielts_listening_scraper.py

爬取 IELTS **听力**测试页面的增强版工具脚本，支持**音频文件自动下载**。

**功能:**
- ✅ 爬取 IELTS 听力测试页面内容
- 🎵 **自动检测和下载音频文件** (MP3, WAV, OGG 等格式)
- 📝 提取标题、段落、问题、链接
- 💾 自动保存为 JSON、Markdown、TXT 三种格式
- 📊 在输出文件中包含音频文件信息和本地路径

**使用方法:**

```bash
# 使用 uv 运行（推荐）
uv run python scripts/ielts_listening_scraper.py

# 使用 python 运行
python scripts/ielts_listening_scraper.py
```

**特性:**
- 自动识别页面中所有音频链接（`<audio>` 标签、`.mp3` 链接等）
- 下载所有音频文件到 `output/ielts_tests/` 目录
- 在 Markdown 和 JSON 输出中记录音频文件位置
- 显示下载进度和文件大小

**输出示例:**
```
output/ielts_tests/
├── cambridge_ielts_20_listening_test_4.json
├── cambridge_ielts_20_listening_test_4.md
├── cambridge_ielts_20_listening_test_4.txt
├── cambridge_ielts_20_listening_test_4_1_audio.mp3  (2.4 MB)
├── cambridge_ielts_20_listening_test_4_2_audio.mp3  (2.4 MB)
├── cambridge_ielts_20_listening_test_4_3_audio.mp3  (2.5 MB)
└── cambridge_ielts_20_listening_test_4_4_audio.mp3  (2.3 MB)
```

## 自定义爬取

### 修改目标 URL

编辑相应脚本文件中的 `main()` 函数：

**阅读测试:**
```python
# 在 ielts_scraper.py 中
def main():
    url = 'https://engnovate.com/ielts-reading-tests/your-test-url/'
    data = scrape_ielts_test(url)
    # ...
```

**听力测试:**
```python
# 在 ielts_listening_scraper.py 中
def main():
    url = 'https://engnovate.com/ielts-listening-tests/your-test-url/'
    data, output_name = scrape_ielts_listening_test(url)
    # ...
```

## 输出位置

所有输出文件保存在: `output/ielts_tests/`

**输出格式:**
- `{test_name}.json` - 完整 JSON 数据（含元数据、音频信息）  
- `{test_name}.md` - Markdown 格式（适合阅读，包含音频文件链接）
- `{test_name}.txt` - 纯文本格式
- `{test_name}_N_audio.mp3` - 下载的音频文件（听力测试）

## Scientific American 播客爬虫 (`sciam_podcast_scraper.py`)

抓取 [Science Quickly](https://www.scientificamerican.com/podcast/science-quickly/) 各期节目的元数据、完整文字稿和 mp3。
只用 HTTP 请求（`FetcherSession`，模拟 Chrome），不需要浏览器。

```bash
# 单期（可重复 --url 传多个）
uv run python scripts/sciam_podcast_scraper.py --url https://www.scientificamerican.com/podcast/episode/are-ai-chatbots-making-us-less-human/

# 批量：抓列表前 3 页（每页约 12 期），同时下载 mp3
uv run python scripts/sciam_podcast_scraper.py --pages 3 --mp3

# 只抓最新 5 期
uv run python scripts/sciam_podcast_scraper.py --limit 5
```

| 参数 | 说明 |
|---|---|
| `--url` | 指定单期 URL，可多次使用；不传则走批量模式 |
| `--pages N` | 批量模式翻页数（默认 1） |
| `--limit N` | 最多处理的期数（默认不限） |
| `--mp3` | 同时下载音频 |
| `--force` | 忽略已有文件重新抓取（默认已抓过的会跳过，可断点续抓） |
| `--delay S` | 请求间隔秒数（默认 1.5） |
| `--out DIR` | 输出目录（默认 `output/sciam/`） |

输出：每期 `{slug}.json`、`{slug}.md`、可选 `{slug}.mp3`，以及汇总的 `index.json`。

> 注意：使用 Clash/Surge 等 fake-IP 代理时，公网域名会解析成 `198.18.x.x`，Scrapling 默认的
> SSRF 保护会拦截 mp3 跳转。脚本会对 megaphone 等白名单域名手动跟随重定向，不需要额外配置。
> 内容版权归 Scientific American 所有，请仅用于个人学习。

## 添加新脚本

将新的工具脚本放入此目录，并在本 README 中添加说明。
