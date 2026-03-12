"""
╔══════════════════════════════════════════════════════════════════╗
║         DNM.EG — ULTIMATE FULL-SITE SCRAPER v3                  ║
║  يسحب كل حاجة بمعنى الكلمة — النسخة النهائية                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import json
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from scrapling.fetchers import Fetcher

BASE_URL  = "https://dnmeg.com"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")
OUTPUT    = f"d:/scripping/dnm_ULTIMATE_{TIMESTAMP}.json"


# ══════════════════════════════════════════════════════════════════════════════
# 1) Shopify JSON API  —  بيانات خام 100%
# ══════════════════════════════════════════════════════════════════════════════

def api_get(path: str):
    """جلب بيانات JSON من Shopify API"""
    url = f"{BASE_URL}/{path.lstrip('/')}"
    try:
        r = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ⚠️  فشل: {url} → {e}")
        return None


def get_all_products():
    """سحب كل المنتجات + كل الـ variants + كل الصور"""
    print("\n  🛍️  سحب المنتجات من Shopify API...")
    all_products = []
    page = 1
    while True:
        data = api_get(f"products.json?limit=250&page={page}")
        if not data:
            break
        products = data.get("products", [])
        if not products:
            break
        all_products.extend(products)
        print(f"     📦 صفحة {page}: {len(products)} منتج")
        if len(products) < 250:
            break
        page += 1
    print(f"  ✅ إجمالي المنتجات: {len(all_products)}")
    return all_products


def get_all_collections():
    """سحب كل الأقسام + منتجات كل قسم"""
    print("\n  📂  سحب الأقسام...")
    data = api_get("collections.json?limit=250")
    if not data:
        return []
    collections = data.get("collections", [])

    for col in collections:
        handle = col.get("handle", "")
        prod_data = api_get(f"collections/{handle}/products.json?limit=250")
        if prod_data:
            col["products_in_collection"] = [
                {"id": p["id"], "title": p["title"], "handle": p["handle"]}
                for p in prod_data.get("products", [])
            ]
        else:
            col["products_in_collection"] = []
        print(f"     📁 {col.get('title')}: {len(col['products_in_collection'])} منتج")

    print(f"  ✅ إجمالي الأقسام: {len(collections)}")
    return collections


def get_all_pages_api():
    """سحب الصفحات الثابتة"""
    print("\n  📄  سحب الصفحات الثابتة...")
    data = api_get("pages.json?limit=250")
    pages = data.get("pages", []) if data else []
    print(f"  ✅ إجمالي الصفحات: {len(pages)}")
    return pages


# ══════════════════════════════════════════════════════════════════════════════
# 2) HTML Crawl  —  كل صفحة + SEO + Schema
# ══════════════════════════════════════════════════════════════════════════════

def scrape_html(url: str) -> dict:
    """كشط صفحة HTML واستخراج كل عناصرها"""
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        return {
            "url": url,
            "status": page.status,
            "meta": {
                "title":       page.css('title::text').get("").strip(),
                "description": page.css('meta[name="description"]::attr(content)').get("").strip(),
                "keywords":    page.css('meta[name="keywords"]::attr(content)').get("").strip(),
                "canonical":   page.css('link[rel="canonical"]::attr(href)').get("").strip(),
                "og_title":    page.css('meta[property="og:title"]::attr(content)').get("").strip(),
                "og_desc":     page.css('meta[property="og:description"]::attr(content)').get("").strip(),
                "og_image":    page.css('meta[property="og:image"]::attr(content)').get("").strip(),
                "og_url":      page.css('meta[property="og:url"]::attr(content)').get("").strip(),
            },
            "headings": {
                f"h{i}": [h.strip() for h in page.css(f'h{i}::text').getall() if h.strip()]
                for i in range(1, 7)
            },
            "all_texts": list(dict.fromkeys([
                t.strip()
                for t in page.css('p::text, span::text, li::text, td::text, div::text, label::text, button::text, a::text').getall()
                if t.strip() and len(t.strip()) > 1
            ])),
            "all_images": list(dict.fromkeys([
                ("https:" + s if s.startswith("//") else urljoin(url, s)).split(" ")[0]
                for s in page.css('img::attr(src), img::attr(data-src)').getall()
                if s
            ])),
            "internal_links": list(dict.fromkeys([
                urljoin(url, h)
                for h in page.css('a::attr(href)').getall()
                if h and not h.startswith(("#", "mailto:", "tel:", "javascript:"))
                and urlparse(urljoin(url, h)).netloc in ("dnmeg.com", "www.dnmeg.com")
            ])),
            "external_links": list(dict.fromkeys([
                urljoin(url, h)
                for h in page.css('a::attr(href)').getall()
                if h and not h.startswith(("#", "mailto:", "tel:", "javascript:"))
                and urlparse(urljoin(url, h)).netloc not in ("dnmeg.com", "www.dnmeg.com", "")
            ])),
            "schema_markup": [
                json.loads(s) for s in page.css('script[type="application/ld+json"]::text').getall()
                if s.strip()
            ] if page.css('script[type="application/ld+json"]::text').getall() else [],
        }
    except Exception as e:
        return {"url": url, "error": str(e)}


def crawl_full_site():
    """زحف كامل على كل صفحات الموقع"""
    print("\n  🌐  زحف كامل على كل صفحات HTML...")
    visited = set()
    queue = {BASE_URL + "/"}
    results = []

    while queue:
        url = queue.pop()
        if url in visited:
            continue
        visited.add(url)

        print(f"     🔍 {url}")
        data = scrape_html(url)
        results.append(data)

        for link in data.get("internal_links", []):
            clean = link.split("?")[0].split("#")[0]
            skip = ["customer_authentication", "cdn.shopify", "cart", "account", "/admin"]
            if clean not in visited and not any(p in clean for p in skip):
                queue.add(clean)

    print(f"  ✅ إجمالي الصفحات: {len(results)}")
    return results


# ══════════════════════════════════════════════════════════════════════════════
# 3) Policies  —  سياسات الموقع
# ══════════════════════════════════════════════════════════════════════════════

def get_policies():
    """سحب نصوص كل السياسات"""
    print("\n  📋  سحب السياسات...")
    policies = {}
    for slug in ["shipping-policy", "refund-policy", "terms-of-service", "privacy-policy"]:
        url = f"{BASE_URL}/policies/{slug}"
        data = scrape_html(url)
        policies[slug] = {
            "url": url,
            "title": data.get("meta", {}).get("title", ""),
            "texts": data.get("all_texts", []),
        }
        print(f"     📋 {slug}")
    return policies


# ══════════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "=" * 60)
    print("🕷️  DNM.EG — ULTIMATE FULL-SITE SCRAPER v3")
    print("=" * 60)

    result = {}

    # ─── Shopify API (بيانات خام) ─────────────────────
    result["all_products"]    = get_all_products()
    result["all_collections"] = get_all_collections()
    result["all_pages_api"]   = get_all_pages_api()

    # ─── HTML Crawl ───────────────────────────────────
    result["policies"]        = get_policies()
    result["html_pages"]      = crawl_full_site()

    # ─── Summary ──────────────────────────────────────
    result["summary"] = {
        "scraped_at":        datetime.now().isoformat(),
        "total_products":    len(result["all_products"]),
        "total_collections": len(result["all_collections"]),
        "total_api_pages":   len(result["all_pages_api"]),
        "total_html_pages":  len(result["html_pages"]),
        "total_policies":    len(result["policies"]),
        "total_variants":    sum(len(p.get("variants", [])) for p in result["all_products"]),
        "total_images":      sum(len(p.get("images", [])) for p in result["all_products"]),
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"🏆  تم بنجاح! الملف: {OUTPUT}")
    print("=" * 60)
    for k, v in result["summary"].items():
        print(f"  {k}: {v}")
    print()


if __name__ == "__main__":
    main()
