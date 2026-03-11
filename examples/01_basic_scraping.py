"""
示例 1: 基础网页抓取
功能：抓取名言网站的名言和作者
"""
from scrapling import Fetcher

# 方法 1: 最简单的方式 - 一行代码获取数据
page = Fetcher.get('https://quotes.toscrape.com/')

# 提取所有名言
quotes = page.css('.quote .text::text').getall()
authors = page.css('.quote .author::text').getall()

print("抓取到的名言：\n")
for quote, author in zip(quotes, authors):
    print(f"📝 {quote}")
    print(f"   — {author}\n")

# 方法 2: 更灵活的方式 - 提取每个名言块
print("\n" + "="*50)
print("更详细的信息：\n")

for quote_elem in page.css('.quote'):
    text = quote_elem.css('.text::text').get()
    author = quote_elem.css('.author::text').get()
    tags = quote_elem.css('.tag::text').getall()
    
    print(f"📝 {text}")
    print(f"   作者: {author}")
    print(f"   标签: {', '.join(tags)}\n")
