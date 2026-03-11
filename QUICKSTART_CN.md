# Scrapling 快速使用指南

## 🎯 你能用 Scrapling 做什么？

### 1️⃣ 数据采集与抓取
- 抓取电商网站的产品信息（价格、描述、评论）
- 采集新闻文章和博客内容
- 收集社交媒体数据
- 抓取搜索引擎结果
- 监控网站变化（价格、库存、内容更新）

### 2️⃣ 绕过反爬虫限制
- ✅ 自动绕过 Cloudflare Turnstile 验证
- ✅ 浏览器指纹伪装（TLS、Headers、User-Agent）
- ✅ JavaScript 渲染页面抓取
- ✅ 自动处理 CAPTCHA（配合第三方服务）

### 3️⃣ 大规模数据采集
- 并发抓取（同时处理多个页面）
- 暂停/恢复功能（长时间爬取支持）
- 代理池自动轮换
- 智能限流和延迟控制

### 4️⃣ 智能自适应爬虫
- 网站改版后自动找回元素
- 基于相似度的元素定位
- 减少维护成本

---

## 🚀 快速开始（3 分钟）

### 方法 1: 命令行使用（不写代码）

```powershell
# 直接抓取网页保存为 Markdown
uv run scrapling extract get 'https://quotes.toscrape.com' quotes.md

# 抓取特定部分（使用 CSS 选择器）
uv run scrapling extract get 'https://quotes.toscrape.com' quotes.md --css-selector '.quote'

# 使用交互式 Shell
uv run scrapling shell
```

### 方法 2: Python 代码（5 行代码抓取数据）

```python
from scrapling import Fetcher

# 一行代码获取网页
page = Fetcher.get('https://quotes.toscrape.com/')

# 提取所有名言
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

### 方法 3: 运行示例代码

```powershell
# 基础抓取示例
uv run python examples/01_basic_scraping.py

# 查看所有示例
cd examples
dir
```

---

## 📖 常用功能速查

### 1. 基础抓取（静态页面）
```python
from scrapling import Fetcher

# GET 请求
page = Fetcher.get('https://example.com')

# POST 请求
page = Fetcher.post('https://example.com/api', data={'key': 'value'})

# 提取数据
titles = page.css('h1::text').getall()      # CSS 选择器
links = page.xpath('//a/@href').getall()    # XPath 选择器
text = page.find_by_text('关键词')           # 文本搜索
```

### 2. 动态页面（JavaScript 渲染）
```python
from scrapling.fetchers import DynamicFetcher

# 使用真实浏览器
page = DynamicFetcher.fetch(
    'https://example.com',
    headless=True,           # 无头模式
    network_idle=True        # 等待网络加载完成
)
data = page.css('.dynamic-content').getall()
```

### 3. 隐身模式（绕过反爬虫）
```python
from scrapling.fetchers import StealthyFetcher

# 自动绕过 Cloudflare
page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True    # 自动解决 Cloudflare
)
```

### 4. 会话管理（保持登录）
```python
from scrapling.fetchers import FetcherSession

with FetcherSession() as session:
    # 登录
    session.post('/login', data={'user': 'xxx', 'pass': 'xxx'})
    
    # 访问需要登录的页面（cookies 自动保持）
    page = session.get('/dashboard')
```

### 5. 构建完整爬虫
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    concurrent_requests = 10  # 并发数
    
    async def parse(self, response: Response):
        for item in response.css('.item'):
            yield {
                "title": item.css('h2::text').get(),
                "price": item.css('.price::text').get(),
            }
        
        # 跟随下一页
        next_page = response.css('.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

# 运行
result = MySpider().start()
result.items.to_json("output.json")  # 保存结果
```

### 6. 代理使用
```python
from scrapling import Fetcher

# 单次请求使用代理
page = Fetcher.get('https://example.com', proxy='http://proxy:8080')

# 代理轮换
from scrapling.engines.toolbelt import ProxyRotator

proxies = ['http://proxy1:8080', 'http://proxy2:8080']
rotator = ProxyRotator(proxies, strategy='cycle')

for url in urls:
    page = Fetcher.get(url, proxy=rotator.get_next())
```

---

## 🎨 数据提取方法

### CSS 选择器
```python
page.css('div.class')                    # 获取元素
page.css('div.class::text').get()        # 获取文本
page.css('div.class::attr(href)').get()  # 获取属性
page.css('div.class').getall()           # 获取所有匹配
```

### XPath 选择器
```python
page.xpath('//div[@class="item"]')
page.xpath('//div[@class="item"]/text()').get()
page.xpath('//a/@href').getall()
```

### BeautifulSoup 风格
```python
page.find_all('div', class_='item')
page.find_by_text('搜索文本')
page.find('h1', id='title')
```

### 导航方法
```python
element = page.css('.item')[0]
element.parent                 # 父元素
element.next_sibling          # 下一个兄弟
element.previous_sibling      # 上一个兄弟
element.children              # 子元素
element.find_similar()        # 相似元素
```

---

## 💡 实用技巧

### 1. 调试技巧
```python
# 查看原始 HTML
print(page.html[:500])

# 查看状态码
print(page.status)

# 查看响应头
print(page.headers)

# 在浏览器中打开结果（Shell 模式）
scrapling shell
>>> page = fetch('https://example.com')
>>> view(page)  # 在浏览器中打开
```

### 2. 性能优化
```python
# 禁用不必要的资源加载（图片、CSS）
page = DynamicFetcher.fetch(
    url,
    disable_resources=True,  # 禁用图片等资源
    headless=True
)

# 使用并发
from scrapling.spiders import Spider
class FastSpider(Spider):
    concurrent_requests = 20  # 提高并发数
    download_delay = 0.1      # 降低延迟
```

### 3. 错误处理
```python
try:
    page = Fetcher.get('https://example.com', timeout=10)
    if page.status != 200:
        print(f"错误状态码: {page.status}")
except Exception as e:
    print(f"请求失败: {e}")
```

---

## 📚 完整示例项目

查看 `examples/` 目录下的完整示例：

1. **基础抓取** - `01_basic_scraping.py`
2. **隐身模式** - `02_stealth_scraping.py`
3. **会话管理** - `03_session_management.py`
4. **爬虫框架** - `04_spider_framework.py`
5. **自适应爬虫** - `05_adaptive_scraping.py`
6. **CLI 工具** - `06_cli_usage.py`
7. **代理轮换** - `07_proxy_rotation.py`

---

## 🔗 更多资源

- 📖 [完整文档](https://scrapling.readthedocs.io/)
- 💬 [Discord 社区](https://discord.gg/EMgGbDceNQ)
- 🐛 [问题反馈](https://github.com/D4Vinci/Scrapling/issues)
- ⭐ [GitHub 仓库](https://github.com/D4Vinci/Scrapling)

---

## ⚠️ 使用注意事项

1. ✅ **合法使用** - 仅用于合法目的
2. ✅ **尊重 robots.txt** - 遵守网站爬虫协议
3. ✅ **控制频率** - 避免对网站造成负担
4. ✅ **使用代理** - 大规模爬取时使用代理池
5. ✅ **处理数据** - 负责任地处理采集的数据

---

**祝你爬虫愉快！🕷️**
