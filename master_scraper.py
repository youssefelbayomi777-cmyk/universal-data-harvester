import sys
import json
import csv
import requests
import argparse
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
from scrapling.fetchers import Fetcher

import warnings
warnings.filterwarnings("ignore")

class UniversalScraper:
    def __init__(self, base_url, max_pages=1000, depth=10):
        self.base_url = base_url.rstrip("/")
        self.base_netloc = urlparse(self.base_url).netloc
        self.max_pages = max_pages
        self.max_depth = depth
        self.visited = set()
        self.results = {
            "target": self.base_url,
            "scraped_at": datetime.now().isoformat(),
            "platform": "generic",
            "api_data": {},
            "html_pages": [],
            "summary": {}
        }
        
        domain = self.base_netloc.replace("www.", "").replace(".", "_")
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        self.out_dir = Path(f"d:/scripping/{domain}_{ts}")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.out_file = self.out_dir / "master_data.json"

    def log(self, msg, icon="ℹ️"):
        print(f"  {icon}  {msg}")

    def http_json(self, path):
        url = urljoin(self.base_url, path)
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if r.status_code == 200: return r.json()
        except: pass
        return None

    def detect_and_scrape_api(self):
        self.log("جاري استكشاف المنصة والـ APIs...")
        
        # Shopify Check
        data = self.http_json("products.json?limit=1")
        if isinstance(data, dict) and "products" in data:
            self.results["platform"] = "shopify"
            self.log("كشف: موقع Shopify - سحب البيانات الخام...", "🛍️")
            self.results["api_data"] = self.scrape_shopify()
            return

        # WordPress Check
        data = self.http_json("wp-json/wp/v2/posts?per_page=1")
        if isinstance(data, list) and len(data) > 0:
            self.results["platform"] = "wordpress"
            self.log("كشف: موقع WordPress - سحب المقالات...", "📝")
            self.results["api_data"] = self.scrape_wordpress()
            return

    def scrape_shopify(self):
        api = {"products": [], "collections": [], "pages": [], "policies": {}}
        # Products
        page = 1
        while True:
            data = self.http_json(f"products.json?limit=250&page={page}")
            if not isinstance(data, dict) or not data.get("products"): break
            api["products"].extend(data["products"])
            if len(data["products"]) < 250: break
            page += 1
            
        # Policies
        for slug in ["shipping-policy", "refund-policy", "terms-of-service", "privacy-policy"]:
            url = f"{self.base_url}/policies/{slug}"
            pol_data = self.scrape_html_page(url)
            if pol_data: api["policies"][slug] = pol_data
        return api

    def scrape_wordpress(self):
        api = {"posts": [], "pages": [], "media": []}
        for type_ in ["posts", "pages", "media"]:
            page = 1
            while True:
                data = self.http_json(f"wp-json/wp/v2/{type_}?per_page=100&page={page}")
                if not isinstance(data, list) or not data: break
                api[type_].extend(data)
                if len(data) < 100: break
                page += 1
        return api

    def scrape_html_page(self, url):
        try:
            page = Fetcher.get(url, stealthy_headers=True)
            return {
                "url": url,
                "meta": {
                    "title": page.css('title::text').get("").strip(),
                    "description": page.css('meta[name="description"]::attr(content)').get("").strip(),
                },
                "headings": {f"h{i}": [h.strip() for h in page.css(f'h{i}::text').getall() if h.strip()] for i in range(1,4)},
                "text": " ".join([t.strip() for t in page.css('p::text, li::text, div::text').getall() if len(t.strip()) > 20]),
                "images": [urljoin(url, src) for src in page.css('img::attr(src)').getall() if src],
                "links": [urljoin(url, href) for href in page.css('a::attr(href)').getall() if href and self.base_netloc in urljoin(url, href)]
            }
        except: return None

    def save(self):
        # تحديث المخلص
        self.results["summary"] = {
            "total_pages": len(self.results["html_pages"]),
            "platform": self.results["platform"],
            "api_items": len(self.results["api_data"].get("products", [])) if self.results["platform"] == "shopify" else len(self.results["api_data"].get("posts", []))
        }
        with open(self.out_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def run_full_crawl(self):
        self.log(f"بدء الزحف الكامل على صفحات HTML...", "🌐")
        queue = [(self.base_url, 0)]
        while queue:
            if self.max_pages and len(self.visited) >= self.max_pages: break
            url, depth = queue.pop(0)
            
            clean_url = url.split("?")[0].split("#")[0].rstrip("/")
            if clean_url in self.visited: continue
            self.visited.add(clean_url)
            
            self.log(f"[{len(self.visited)}] كشط: {url}", "🔍")
            data = self.scrape_html_page(url)
            if data:
                self.results["html_pages"].append(data)
                self.save() # حفظ دوري
            
            if depth < self.max_depth and data and "links" in data:
                for link in data["links"]:
                    if link not in self.visited:
                        queue.append((link, depth + 1))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--pages", type=int, default=1000)
    args = parser.parse_args()
    
    scraper = UniversalScraper(args.url, max_pages=args.pages)
    scraper.detect_and_scrape_api()
    scraper.run_full_crawl()
    scraper.save()
