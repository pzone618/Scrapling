"""
示例 4: 构建完整的爬虫（Spider）
功能：使用 Spider 框架进行大规模并发爬取，支持暂停/恢复
"""
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    """抓取所有名言的爬虫"""
    
    name = "quotes_spider"
    start_urls = ["https://quotes.toscrape.com/"]
    
    # 配置
    concurrent_requests = 5      # 并发请求数
    download_delay = 0.5         # 请求间隔（秒）
    
    async def parse(self, response: Response):
        """解析每个页面"""
        # 提取当前页面的所有名言
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
                "tags": quote.css('.tag::text').getall(),
            }
        
        # 查找下一页链接
        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            # 跟随下一页链接
            yield response.follow(next_page)

# 运行爬虫
if __name__ == '__main__':
    print("🕷️  启动 Quotes Spider...\n")
    
    # 方式 1: 直接运行（不保存进度）
    result = QuotesSpider().start()
    
    print(f"\n✅ 爬取完成！")
    print(f"📊 统计信息:")
    print(f"   - 总条目数: {len(result.items)}")
    print(f"   - 已请求页面: {result.stats.get('request_count', 0)}")
    
    # 保存结果
    result.items.to_json("quotes_output.json")
    print(f"\n💾 结果已保存到: quotes_output.json")
    
    # 显示前 3 条数据
    print(f"\n前 3 条数据预览:")
    for i, item in enumerate(result.items[:3], 1):
        print(f"  {i}. {item['text'][:50]}... - {item['author']}")
    
    # 方式 2: 支持暂停/恢复（按 Ctrl+C 暂停，重新运行继续）
    # result = QuotesSpider(crawldir="./crawl_data").start()
