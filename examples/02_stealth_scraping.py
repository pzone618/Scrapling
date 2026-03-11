"""
示例 2: 隐身模式抓取（绕过反爬虫）
功能：使用 StealthyFetcher 绕过 Cloudflare 等保护
"""
from scrapling.fetchers import StealthyFetcher

print("启动隐身浏览器，绕过 Cloudflare...")

# 使用隐身模式抓取受保护的网站
page = StealthyFetcher.fetch(
    'https://nopecha.com/demo/cloudflare',
    headless=True,              # 无头模式（不显示浏览器窗口）
    solve_cloudflare=True,      # 自动解决 Cloudflare 验证
    network_idle=True           # 等待网络空闲
)

# 提取内容
content = page.css('#padded_content').get()
links = page.css('#padded_content a::text').getall()

print("\n✅ 成功绕过 Cloudflare！")
print(f"\n找到的链接: {links}\n")
print("页面部分内容:")
print(content[:500] if content else "无内容")
