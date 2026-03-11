"""
示例 5: 智能自适应爬虫（网站改版后仍能找到元素）
功能：使用 adaptive 模式，即使网站结构改变也能找到目标元素
"""
from scrapling.fetchers import StealthyFetcher

# 启用自适应模式
StealthyFetcher.adaptive = True

print("第一次访问：保存元素特征...")

# 第一次抓取 - 保存元素特征
page = StealthyFetcher.fetch('https://quotes.toscrape.com/', headless=True)

# 使用 auto_save=True 保存元素的特征
products = page.css('.quote', auto_save=True)  
print(f"✓ 找到 {len(products)} 个名言块，已保存特征\n")

# 模拟网站改版后的情况
print("="*60)
print("假设网站改版了，CSS 选择器可能失效...")
print("使用 adaptive=True 通过特征相似度找回元素：\n")

# 第二次访问 - 使用自适应模式
page2 = StealthyFetcher.fetch('https://quotes.toscrape.com/', headless=True)

# 即使选择器改变，adaptive=True 会根据保存的特征找到相似元素
quotes = page2.css('.quote', adaptive=True)  
print(f"✅ 自适应模式找到 {len(quotes)} 个相似元素")

# 或者手动查找相似元素
if quotes:
    first_quote = quotes[0]
    similar = first_quote.find_similar()
    print(f"✓ 找到 {len(similar)} 个与第一个名言相似的元素")

print("\n💡 提示：这个功能在网站频繁改版时非常有用！")
