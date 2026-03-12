# Scrapling: Complete Documentation & Guide

Scrapling is a modern, high-performance web scraping and crawling framework for Python. It is designed to handle everything from simple HTTP requests to complex, anti-bot-protected crawls with features like adaptive parsing and AI-ready integration.

---

## 🚀 1. Overview
Scrapling stands out by combining speed, stealth, and "intelligence" (adaptive parsing).
- **Stealth**: Built-in bypass for Cloudflare Turnstile, browser impersonation (TLS/Headers).
- **Adaptability**: Can relocate elements after website design changes.
- **Performance**: Optimized for speed (10x faster JSON serialization) and low memory usage.
- **AI-Ready**: Native MCP server to provide targeted data to LLMs.

---

## 🛠 2. Installation
Scrapling requires **Python 3.10+**.

```bash
# Basic installation (Parser only)
pip install scrapling

# Full installation (Includes fetcher dependencies and CLI)
pip install "scrapling[all]"
```

---

## 🌐 3. Fetchers
Fetchers are responsible for retrieving website content. Scrapling offers three main types:

### A. `Fetcher` (Standard HTTP)
Fast and lightweight. Best for simple sites without heavy protection.
- Supports HTTP/1.1, HTTP/2, and HTTP/3.
- Mimics browser TLS fingerprints and headers.

### B. `StealthyFetcher` (Anti-Bot Bypass)
Designed to crawl under the radar.
- Bypasses Cloudflare Turnstile and Interstitial pages out of the box.
- Rotates fingerprints and handles session management automatically.

### C. `DynamicFetcher` (Full Browser)
Uses Playwright/Chrome for Javascript-heavy applications.
- Supports headless and headful modes.
- Can wait for network idle or specific selectors.

### ⚡ Async Support
Every fetcher has an async counterpart for high-performance operations:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.get("https://example.com")
```

---

## 🔍 4. Parsing & Selection
Scrapling provides a powerful selector engine that supports standard and advanced methods.

### Basic Selection
```python
# CSS Selectors
page.css(".product-title")

# XPath Selectors
page.xpath("//h1/text()")

# Find/Find All (BeautifulSoup-like)
page.find("section", id="products")
page.find_all("h3", string=re.compile(r"Product \d"))
```

### 🧠 Adaptive Scraping (The "Magic")
Scrapling can "learn" an element's path to survive website redesigns.
1. **Save Pattern**: Find an element and save its "DNA".
   ```python
   # auto_save=True stores the element structure
   product = page.css(".price", auto_save=True)
   ```
2. **Retrieve Later**: Even if the class `.price` is changed to `.cost`, Scrapling can find it.
   ```python
   # adaptive=True uses similarity algorithms to relocate the element
   product = page.css(".price", adaptive=True)
   ```

### 🔄 `find_similar()`
Inspired by AutoScraper, this finds elements with similar DOM patterns.
```python
first_product = page.find("h3", string="Product 1")
all_products = first_product.find_similar()
```

---

## 🕸 5. The Spiders Framework
Build full-scale crawlers with persistent sessions and Scrapy-like architecture.

### Basic Spider Structure
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "my_crawler"
    start_urls = ["https://example.com/shop"]

    async def parse(self, response: Response):
        # Extract data
        for item in response.css(".item"):
            yield {"title": item.css("h2::text").get()}

        # Follow links
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

MySpider().start()
```

### Key Spider Features:
- **Concurrency**: Per-domain throttling and concurrent request limits.
- **Pause & Resume**: Graceful shutdowns save state to disk; restart to resume.
- **Streaming**: Stream results in real-time using `async for item in spider.stream()`.

---

## 🐚 6. CLI & Interactive Shell
Scrapling includes a powerful interactive shell for testing selectors.

```bash
# Launch shell for a URL
scrapling shell https://example.com

# Use specific fetchers in shell
scrapling shell https://example.com --stealthy
```
**Shortcut Commands in Shell:**
- `view()`: Open the page in your browser.
- `fetch(url)`: Fetch a new URL in the same session.
- `page.css(...)`: Test your selectors instantly.

---

## 🤖 7. AI Integration (MCP Server)
Scrapling includes a built-in **Model Context Protocol (MCP)** server. This allows LLMs (like Claude or Cursor) to act as autonomous scrapers.

**How it helps AI:**
- **Token Efficiency**: Instead of sending the whole HTML to the LLM, the MCP server extracts specific content first.
- **Capabilities**: Gives AI the ability to `scrape_url`, `click_element`, or `search_data` directly.

**Setup for Claude Desktop:**
Add the following to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "scrapling": {
    "command": "python",
    "args": ["-m", "scrapling.mcp"]
  }
}
```

---

## 🛡 8. Advanced Features
- **Proxy Rotation**: Built-in `ProxyRotator` for cycling through lists of proxies.
- **Custom Headers**: Realistic header generation based on real browser data.
- **Blocked Detection**: Customizable logic to detect if a request was blocked and retry automatically.

---

## 📝 9. Summary Table
| Feature | Scrapling | Scrapy | BeautifulSoup |
| :--- | :--- | :--- | :--- |
| **Async Support** | Native (Modern) | Twisted (Legacy) | No (Synchronous) |
| **Anti-Bot Bypass** | Built-in (Stealthy) | Requires Middleware | No |
| **Adaptive Parsing** | Yes (AI Similarity) | No | No |
| **JS Rendering** | Playwright/Chrome | Requires Scrapy-Playwright | No |
| **Persistence** | Pause/Resume | Jobdir | No |

---

## 🔗 10. Useful Links
- **Official Docs**: [scrapling.readthedocs.io](https://scrapling.readthedocs.io/)
- **GitHub**: [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling)
- **Discord**: [Join Support Server](https://discord.gg/EMgGbDceNQ)
