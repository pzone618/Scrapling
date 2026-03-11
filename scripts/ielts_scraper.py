"""
IELTS 阅读测试爬虫 - 规范版本
输出目录: output/ielts_tests/
"""
from scrapling.fetchers import StealthyFetcher
import json
from pathlib import Path
from datetime import datetime

# 配置路径
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "ielts_tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def scrape_ielts_test(url, output_name=None):
    """
    爬取 IELTS 阅读测试
    
    Args:
        url: IELTS 测试页面 URL
        output_name: 输出文件名（不含扩展名），默认自动生成
    
    Returns:
        dict: 爬取的数据
    """
    print(f"正在爬取: {url}\n")
    
    # 使用 StealthyFetcher 获取页面
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True, wait=2)
    
    # 提取标题
    title = page.css('h1::text').get() or page.css('title::text').get() or "IELTS Reading Test"
    print(f"📖 标题: {title}\n")
    
    # 提取所有段落文本
    paragraphs = []
    for p in page.css('p::text').getall():
        text = p.strip()
        if text and len(text) > 20:  # 过滤掉太短的文本
            paragraphs.append(text)
    
    # 提取所有标题（h2, h3, h4）
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
    
    # 提取所有链接（可能用于翻页）
    links = []
    for a in page.css('a'):
        href = a.attrib.get('href', '')
        text = a.css('::text').get('').strip()
        if href and text:
            links.append({"text": text, "href": href})
    
    print(f"✓ 提取了 {len(paragraphs)} 段文本")
    print(f"✓ 提取了 {len(headings)} 个标题")
    print(f"✓ 提取了 {len(questions)} 个问题/列表项")
    print(f"✓ 提取了 {len(links)} 个链接\n")
    
    # 组织数据
    data = {
        "metadata": {
            "url": url,
            "title": title,
            "scraped_at": datetime.now().isoformat(),
            "scraper_version": "1.0"
        },
        "content": {
            "headings": headings,
            "paragraphs": paragraphs,
            "questions": questions,
            "links": links[:20]  # 只保留前20个链接
        },
        "stats": {
            "headings": len(headings),
            "paragraphs": len(paragraphs),
            "questions": len(questions),
            "links": len(links)
        }
    }
    
    return data

def save_data(data, output_name=None):
    """
    保存数据为多种格式到 output/ielts_tests/ 目录
    
    Args:
        data: 要保存的数据
        output_name: 输出文件名（不含扩展名）
    
    Returns:
        dict: 保存的文件路径
    """
    if output_name is None:
        # 从标题生成文件名
        title = data['metadata']['title']
        output_name = title.lower().replace(' ', '_').replace('-', '_')
        # 移除特殊字符
        output_name = ''.join(c for c in output_name if c.isalnum() or c == '_')
    
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
        f.write(f"**爬取时间:** {data['metadata']['scraped_at']}  \n\n")
        f.write("---\n\n")
        
        if data['content']['headings']:
            f.write("## 📑 目录结构\n\n")
            for h in data['content']['headings']:
                f.write(f"- {h}\n")
            f.write("\n---\n\n")
        
        f.write("## 📝 内容\n\n")
        for para in data['content']['paragraphs']:
            f.write(f"{para}\n\n")
        
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
        f.write(f"爬取时间: {data['metadata']['scraped_at']}\n\n")
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
    print(f"  - 标题数: {data['stats']['headings']}")
    print(f"  - 段落数: {data['stats']['paragraphs']}")
    print(f"  - 问题数: {data['stats']['questions']}")
    print(f"  - 链接数: {data['stats']['links']}")
    
    if data['content']['headings']:
        print(f"\n📑 前5个标题:")
        for i, h in enumerate(data['content']['headings'][:5], 1):
            print(f"  {i}. {h}")
    
    if data['content']['paragraphs']:
        print(f"\n📝 第一段内容:")
        preview = data['content']['paragraphs'][0][:200]
        print(f"  {preview}..." if len(data['content']['paragraphs'][0]) > 200 else f"  {preview}")
    
    if data['content']['questions']:
        print(f"\n❓ 前5个问题:")
        for i, q in enumerate(data['content']['questions'][:5], 1):
            print(f"  {i}. {q}")

def main():
    """主函数"""
    # 默认 URL
    url = 'https://engnovate.com/ielts-reading-tests/cambridge-ielts-20-academic-reading-test-4/'
    
    # 可以修改这里来爬取不同的页面
    # url = 'https://engnovate.com/ielts-reading-tests/cambridge-ielts-20-academic-reading-test-1/'
    
    try:
        # 爬取数据
        data = scrape_ielts_test(url)
        
        # 保存数据（自动命名）
        saved_files = save_data(data)
        
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
