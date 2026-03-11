"""
示例 7: 代理轮换
功能：自动轮换代理 IP，避免被封禁
"""
from scrapling.fetchers import FetcherSession
from scrapling.engines.toolbelt import ProxyRotator

# 设置代理列表
proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
]

# 创建代理轮换器
rotator = ProxyRotator(proxies, strategy='cycle')  # 循环使用

print("使用代理轮换器进行多次请求...\n")

with FetcherSession() as session:
    for i in range(3):
        # 每次请求使用不同的代理
        proxy = rotator.get_next()
        print(f"请求 {i+1}: 使用代理 {proxy}")
        
        # page = session.get('https://httpbin.org/ip', proxy=proxy)
        # ip = page.json()['origin']
        # print(f"  → 当前 IP: {ip}\n")

print("✅ 代理轮换演示完成")
print("\n💡 提示：在实际使用中，替换为你的真实代理地址")
