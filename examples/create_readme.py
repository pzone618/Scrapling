"""
Scrapling 使用示例集合
========================

本目录包含 Scrapling 的各种使用示例，从基础到高级。

## 📚 示例列表

### 基础示例
- `01_basic_scraping.py` - 基础网页数据抓取
- `02_stealth_scraping.py` - 隐身模式绕过反爬虫
- `03_session_management.py` - 会话管理和 Cookie 保持

### 高级示例
- `04_spider_framework.py` - 完整的爬虫框架（并发、暂停/恢复）
- `05_adaptive_scraping.py` - 智能自适应爬虫（网站改版自动适配）
- `06_cli_usage.py` - 命令行工具使用指南
- `07_proxy_rotation.py` - 代理轮换和 IP 管理

## 🚀 快速开始

### 运行单个示例
```bash
# 基础抓取
uv run python examples/01_basic_scraping.py

# 隐身模式（需要先安装浏览器）
uv run scrapling install
uv run python examples/02_stealth_scraping.py

# 完整爬虫
uv run python examples/04_spider_framework.py
```

### 使用命令行工具（无需编程）
```bash
# 启动交互式 Shell
uv run scrapling shell

# 直接提取网页到文件
uv run scrapling extract get 'https://quotes.toscrape.com' output.md
```

## 📖 更多资源

- 完整文档: https://scrapling.readthedocs.io/
- GitHub 仓库: https://github.com/D4Vinci/Scrapling
- Discord 社区: https://discord.gg/EMgGbDceNQ

## 💡 常见使用场景

### 1. 数据采集
- 电商产品信息抓取
- 新闻文章采集
- 社交媒体数据
- 搜索引擎结果

### 2. 自动化任务
- 网站监控（价格、库存等）
- 定期数据更新
- 内容聚合
- 自动化测试

### 3. 研究和分析
- 市场调研
- 舆情分析
- 学术研究数据采集
- 竞品分析

## ⚠️ 注意事项

1. **遵守法律法规** - 仅用于合法用途
2. **尊重 robots.txt** - 遵守网站爬虫规则
3. **控制频率** - 避免对目标网站造成负担
4. **使用代理** - 大规模爬取时使用代理池

---
Happy Scraping! 🕷️
"""

with open('c:\\Work\\dev\\Scrapling\\examples\\README.md', 'w', encoding='utf-8') as f:
    f.write(__doc__)

print("✅ 已创建 examples/README.md")
