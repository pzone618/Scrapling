"""
示例 6: 命令行工具使用
功能：不写代码，直接在命令行抓取数据
"""

# 这个文件展示如何使用 Scrapling 的 CLI 工具
# 直接在终端运行以下命令：

commands = """
# 1. 启动交互式爬虫 Shell（类似 IPython）
uv run scrapling shell

# 2. 直接提取网页内容到文件（不写代码）

# 提取为 Markdown 格式
uv run scrapling extract get 'https://quotes.toscrape.com' quotes.md

# 提取为纯文本
uv run scrapling extract get 'https://quotes.toscrape.com' quotes.txt

# 提取 HTML 格式
uv run scrapling extract get 'https://quotes.toscrape.com' quotes.html

# 使用 CSS 选择器提取特定部分
uv run scrapling extract get 'https://quotes.toscrape.com' quotes.md --css-selector '.quote'

# 使用浏览器模式（处理 JavaScript）
uv run scrapling extract fetch 'https://example.com' content.md --no-headless

# 使用隐身模式绕过反爬虫
uv run scrapling extract stealthy-fetch 'https://protected-site.com' content.html --solve-cloudflare

# 伪装成特定浏览器
uv run scrapling extract get 'https://example.com' content.txt --impersonate chrome

# 3. 安装浏览器依赖（如果还没安装）
uv run scrapling install

# 4. 运行 MCP 服务器（与 AI 工具集成）
uv run scrapling mcp
"""

print("Scrapling CLI 工具使用指南")
print("="*60)
print(commands)
print("\n💡 提示：直接在终端（PowerShell/CMD）中复制粘贴上面的命令即可使用")
