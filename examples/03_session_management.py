"""
示例 3: 使用会话保持登录状态
功能：使用 Session 在多个请求间保持 cookies 和状态
"""
from scrapling.fetchers import FetcherSession

print("使用会话进行多次请求...")

# 创建一个会话（会保持 cookies）
with FetcherSession(impersonate='chrome') as session:
    # 第一个请求 - 访问首页
    page1 = session.get('https://quotes.toscrape.com/')
    print(f"✓ 首页标题: {page1.css('h1 a::text').get()}")
    
    # 第二个请求 - 访问登录页（使用同一会话）
    login_page = session.get('https://quotes.toscrape.com/login')
    csrf_token = login_page.css('input[name="csrf_token"]::attr(value)').get()
    print(f"✓ 获取到 CSRF token: {csrf_token[:20]}...")
    
    # 第三个请求 - 可以提交登录表单
    # login_result = session.post('https://quotes.toscrape.com/login', data={
    #     'username': 'your_username',
    #     'password': 'your_password',
    #     'csrf_token': csrf_token
    # })
    
    print("\n✅ 会话演示完成！所有请求共享相同的 cookies")
