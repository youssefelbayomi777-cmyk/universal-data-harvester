"""
╔══════════════════════════════════════════════════════════════════╗
║          🕷️ UNIVERSAL SITE SCRAPER — ماكينة الكشط الشاملة       ║
║  تشتغل مع أي موقع في العالم وتسحب كل حاجة:                    ║
║  ✅ كل صفحات الموقع (HTML Crawl)                                ║
║  ✅ كل النصوص / العناوين / الصور / الروابط                      ║
║  ✅ بيانات SEO كاملة (meta, canonical, og, schema)              ║
║  ✅ كشف تلقائي لنوع الموقع (Shopify / WordPress / عادي)         ║
║  ✅ استخراج بيانات Shopify الخام لو الموقع Shopify              ║
║  ✅ استخراج مقالات WordPress لو الموقع WordPress                ║
║  ✅ استخراج جداول / قوائم / نماذج / فيديوهات                   ║
║  ✅ تصدير JSON + CSV                                             ║
╚══════════════════════════════════════════════════════════════════╝

الاستخدام:
    py -3.11 universal_scraper.py https://example.com
    py -3.11 universal_scraper.py https://example.com --depth 3
    py -3.11 universal_scraper.py https://example.com --max-pages 100
"""

import sys
import json
import csv
import requests
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlencode
from pathlib import Path
from scrapling.fetchers import Fetcher



# ══════════════════════════════════════════════════════════════════════════════
# UTILS
# ══════════════════════════════════════════════════════════════════════════════

def clean_url(url: str) -> str:
    return url.split("?")[0].split("#")[0].rstrip("/")


def is_internal(url: str, base_netloc: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "") == base_netloc.replace("www.", "")


def http_get_json(url: str) -> dict | None:
    """طلب JSON عادي (للـ APIs)"""
    try:
        r = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }, timeout=20)
        if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
            return r.json()
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_platform(base_url: str, first_page) -> str:
    """اكتشاف منصة الموقع تلقائياً"""
    html_lower = str(first_page.content).lower() if hasattr(first_page, 'content') else ""

    if "shopify.com" in html_lower or "cdn.shopify" in html_lower or "myshopify" in html_lower:
        return "shopify"
    if "wp-content" in html_lower or "wp-includes" in html_lower or "wordpress" in html_lower:
        return "wordpress"
    if "woocommerce" in html_lower:
        return "woocommerce"
    if "magento" in html_lower:
        return "magento"
    if "drupal" in html_lower:
        return "drupal"

    # Try Shopify products.json endpoint
    data = http_get_json(f"{base_url}/products.json?limit=1")
    if data and "products" in data:
        return "shopify"

    # Try WordPress API
    data = http_get_json(f"{base_url}/wp-json/wp/v2/posts?per_page=1")
    if data and isinstance(data, list):
        return "wordpress"

    return "generic"


# ══════════════════════════════════════════════════════════════════════════════
# HTML PAGE SCRAPER — يسحب كل حاجة من أي صفحة
# ══════════════════════════════════════════════════════════════════════════════

def scrape_page(url: str, base_netloc: str) -> dict:
    """سحب كل محتوى صفحة HTML"""
    try:
        page = Fetcher.get(url, stealthy_headers=True)

        # ── Meta & SEO ─────────────────────────────────────────
        meta = {
            "title":        page.css('title::text').get("").strip(),
            "description":  page.css('meta[name="description"]::attr(content)').get("").strip(),
            "keywords":     page.css('meta[name="keywords"]::attr(content)').get("").strip(),
            "robots":       page.css('meta[name="robots"]::attr(content)').get("").strip(),
            "canonical":    page.css('link[rel="canonical"]::attr(href)').get("").strip(),
            "og_title":     page.css('meta[property="og:title"]::attr(content)').get("").strip(),
            "og_desc":      page.css('meta[property="og:description"]::attr(content)').get("").strip(),
            "og_image":     page.css('meta[property="og:image"]::attr(content)').get("").strip(),
            "og_type":      page.css('meta[property="og:type"]::attr(content)').get("").strip(),
            "og_url":       page.css('meta[property="og:url"]::attr(content)').get("").strip(),
            "twitter_card": page.css('meta[name="twitter:card"]::attr(content)').get("").strip(),
            "twitter_title":page.css('meta[name="twitter:title"]::attr(content)').get("").strip(),
            "author":       page.css('meta[name="author"]::attr(content)').get("").strip(),
            "lang":         page.css('html::attr(lang)').get("").strip(),
        }

        # ── Headings ───────────────────────────────────────────
        headings = {
            f"h{i}": [h.strip() for h in page.css(f'h{i}::text').getall() if h.strip()]
            for i in range(1, 7)
        }

        # ── Full Text (مرتب وبدون تكرار) ──────────────────────
        all_texts = list(dict.fromkeys([
            t.strip()
            for t in page.css(
                'p::text, span::text, li::text, td::text, th::text, div::text, '
                'label::text, button::text, a::text, strong::text, em::text, '
                'blockquote::text, caption::text'
            ).getall()
            if t.strip() and len(t.strip()) > 1
        ]))

        # ── Images (كل الصور بالرابط الكامل) ─────────────────
        images = []
        for src in page.css('img::attr(src), img::attr(data-src), img::attr(data-lazy-src)').getall():
            if src:
                full = urljoin(url, src.split(" ")[0])
                if full.startswith("//"):
                    full = "https:" + full
                if full not in images:
                    images.append(full)

        # ── Videos ────────────────────────────────────────────
        videos = list(set([
            urljoin(url, src) for src in
            page.css('video::attr(src), source::attr(src), iframe::attr(src)').getall()
            if src and ("youtube" in src or "vimeo" in src or ".mp4" in src or "video" in src)
        ]))

        # ── Links (داخلي/خارجي) ───────────────────────────────
        internal_links, external_links = [], []
        for href in page.css('a::attr(href)').getall():
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            full = urljoin(url, href)
            if is_internal(full, base_netloc):
                if full not in internal_links:
                    internal_links.append(full)
            else:
                if full not in external_links:
                    external_links.append(full)

        # ── Tables (جداول) ────────────────────────────────────
        tables = []
        for table in page.css('table'):
            rows = []
            for tr in table.css('tr'):
                cells = [td.css('::text').get("").strip() for td in tr.css('td, th')]
                if any(cells):
                    rows.append(cells)
            if rows:
                tables.append(rows)

        # ── Lists (قوائم) ─────────────────────────────────────
        lists = []
        for ul in page.css('ul, ol'):
            items = [li.css('::text').get("").strip() for li in ul.css('li') if li.css('::text').get("").strip()]
            if items:
                lists.append(items)

        # ── Forms (نماذج الإدخال) ─────────────────────────────
        forms = []
        for form in page.css('form'):
            forms.append({
                "action": urljoin(url, form.attrib.get("action", "")),
                "method": form.attrib.get("method", "get"),
                "inputs": [
                    {"name": i.attrib.get("name",""), "type": i.attrib.get("type","text")}
                    for i in form.css('input, textarea, select')
                ],
            })

        # ── Schema / JSON-LD (بيانات هيكلية) ─────────────────
        schema = []
        for s in page.css('script[type="application/ld+json"]::text').getall():
            try:
                schema.append(json.loads(s.strip()))
            except Exception:
                pass

        # ── Navigation ────────────────────────────────────────
        nav_links = [
            {"text": a.css('::text').get("").strip(), "href": urljoin(url, a.attrib.get("href",""))}
            for a in page.css('nav a, header a, [role="navigation"] a')
            if a.css('::text').get("").strip()
        ]

        return {
            "url":            url,
            "status":         page.status,
            "meta":           meta,
            "headings":       headings,
            "all_texts":      all_texts,
            "images":         images,
            "videos":         videos,
            "internal_links": internal_links,
            "external_links": external_links,
            "tables":         tables,
            "lists":          lists,
            "forms":          forms,
            "schema_markup":  schema,
            "navigation":     nav_links,
        }
    except Exception as e:
        return {"url": url, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM-SPECIFIC API SCRAPERS
# ══════════════════════════════════════════════════════════════════════════════

def scrape_shopify(base_url: str) -> dict:
    """سحب كل بيانات Shopify الخام"""
    print("  🛍️  كشف: موقع Shopify — جاري سحب كل بيانات API...")
    result = {}

    # Products
    all_prods, page = [], 1
    while True:
        data = http_get_json(f"{base_url}/products.json?limit=250&page={page}")
        if not data:
            break
        prods = data.get("products", [])
        if not prods:
            break
        all_prods.extend(prods)
        print(f"     📦 صفحة {page}: {len(prods)} منتج")
        if len(prods) < 250:
            break
        page += 1
    result["products"] = all_prods
    print(f"  ✅ إجمالي المنتجات: {len(all_prods)}")

    # Collections
    data = http_get_json(f"{base_url}/collections.json?limit=250")
    cols = data.get("collections", []) if data else []
    for col in cols:
        handle = col.get("handle", "")
        prod_data = http_get_json(f"{base_url}/collections/{handle}/products.json?limit=250")
        col["products_in_collection"] = [
            {"id": p["id"], "title": p["title"], "handle": p["handle"]}
            for p in (prod_data.get("products", []) if prod_data else [])
        ]
    result["collections"] = cols
    print(f"  ✅ إجمالي الأقسام: {len(cols)}")

    # Pages
    data = http_get_json(f"{base_url}/pages.json?limit=250")
    result["pages"] = data.get("pages", []) if data else []
    print(f"  ✅ إجمالي الصفحات الثابتة: {len(result['pages'])}")

    # Blogs
    data = http_get_json(f"{base_url}/blogs.json?limit=250")
    result["blogs"] = data.get("blogs", []) if data else []

    # Meta fields / shop info
    shop_data = http_get_json(f"{base_url}/shop.json")
    result["shop_info"] = shop_data.get("shop", {}) if shop_data else {}

    # Policies (Shopify-specific)
    print("  📋  سحب سياسات الموقع...")
    policy_slugs = ["shipping-policy", "refund-policy", "terms-of-service", "privacy-policy"]
    policies = {}
    for slug in policy_slugs:
        pol_url = f"{base_url}/policies/{slug}"
        pol = scrape_page(pol_url, urlparse(base_url).netloc)
        policies[slug] = {
            "url":   pol_url,
            "title": pol.get("meta", {}).get("title", ""),
            "texts": pol.get("all_texts", []),
        }
        print(f"     📋 {slug}: {len(policies[slug]['texts'])} نص")
    result["policies"] = policies

    return result


def scrape_wordpress(base_url: str) -> dict:
    """سحب كل بيانات WordPress الخام"""
    print("  📝  كشف: موقع WordPress — جاري سحب كل مقالات API...")
    result = {}
    wp_base = f"{base_url}/wp-json/wp/v2"

    def get_all(endpoint):
        items, page = [], 1
        while True:
            data = http_get_json(f"{wp_base}/{endpoint}?per_page=100&page={page}")
            if not data or not isinstance(data, list):
                break
            items.extend(data)
            if len(data) < 100:
                break
            page += 1
        return items

    result["posts"]      = get_all("posts")
    result["pages"]      = get_all("pages")
    result["categories"] = get_all("categories")
    result["tags"]       = get_all("tags")
    result["media"]      = get_all("media")
    result["authors"]    = get_all("users")

    print(f"  ✅ مقالات: {len(result['posts'])}, صفحات: {len(result['pages'])}, ميديا: {len(result['media'])}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# FULL SITE CRAWLER
# ══════════════════════════════════════════════════════════════════════════════

def full_crawl(base_url: str, max_pages: int, max_depth: int) -> list:
    """زحف على كل صفحات الموقع"""
    print(f"\n  🌐  بدء الزحف الكامل (max={max_pages} صفحة, depth={max_depth})...")
    base_netloc = urlparse(base_url).netloc

    visited  = set()
    queue    = [(base_url, 0)]   # (url, depth)
    results  = []

    skip_patterns = [
        "login", "logout", "register", "account", "checkout",
        "admin", "wp-login", "cart", "cdn.shopify", "customer_auth"
    ]

    while queue and len(results) < max_pages:
        url, depth = queue.pop(0)
        clean = clean_url(url)

        if clean in visited:
            continue
        visited.add(clean)

        if any(p in clean for p in skip_patterns):
            continue

        print(f"     🔍 [{depth}] {url}")
        data = scrape_page(url, base_netloc)
        results.append(data)

        # اتبع الروابط للعمق التالي
        if depth < max_depth:
            for link in data.get("internal_links", []):
                lclean = clean_url(link)
                if lclean not in visited and not any(p in lclean for p in skip_patterns):
                    queue.append((link, depth + 1))

    print(f"  ✅ إجمالي الصفحات المسحوبة: {len(results)}")
    return results


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════════════════════════════════════════

def export_csv(pages: list, output_prefix: str):
    """تصدير ملخص CSV"""
    csv_path = f"{output_prefix}.csv"
    rows = []
    for p in pages:
        if "error" in p:
            continue
        rows.append({
            "url":         p.get("url", ""),
            "status":      p.get("status", ""),
            "title":       p.get("meta", {}).get("title", ""),
            "description": p.get("meta", {}).get("description", ""),
            "h1":          " | ".join(p.get("headings", {}).get("h1", [])),
            "images_count": len(p.get("images", [])),
            "links_in":    len(p.get("internal_links", [])),
            "links_out":   len(p.get("external_links", [])),
            "schema":      "✅" if p.get("schema_markup") else "❌",
        })
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"  📊 CSV: {csv_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="🕷️ Universal Site Scraper — ماكينة الكشط الشاملة")
    parser.add_argument("url", nargs="?", help="رابط الموقع")
    parser.add_argument("--depth",     type=int, default=5,   help="عمق الزحف (افتراضي: 5)")
    parser.add_argument("--max-pages", type=int, default=500, help="الحد الأقصى للصفحات (افتراضي: 500)")
    args = parser.parse_args()

    # ── الحصول على الرابط ─────────────────────────────────────
    base_url = args.url
    if not base_url:
        base_url = input("\n  🌐 أدخل رابط الموقع (مثال: https://example.com): ").strip()
    if not base_url.startswith("http"):
        base_url = "https://" + base_url
    base_url = base_url.rstrip("/")

    domain   = urlparse(base_url).netloc.replace("www.", "").replace(".", "_")
    ts       = datetime.now().strftime("%Y%m%d_%H%M")
    out_dir  = Path(f"d:/scripping/{domain}_{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = str(out_dir / "full_data.json")
    out_csv  = str(out_dir / "pages_summary")

    print("\n" + "═" * 60)
    print(f"  🕷️  UNIVERSAL SCRAPER")
    print(f"  🌐  الموقع : {base_url}")
    print(f"  📁  المجلد : {out_dir}")
    print("═" * 60)

    result = {
        "target":   base_url,
        "scraped_at": datetime.now().isoformat(),
    }

    # ── اكتشاف المنصة ─────────────────────────────────────────
    print("\n  🔎  اكتشاف نوع الموقع...")
    try:
        first = Fetcher.get(base_url, stealthy_headers=True)
        platform = detect_platform(base_url, first)
    except Exception:
        platform = "generic"
    print(f"  💡  النوع المكتشف: {platform.upper()}")
    result["platform"] = platform

    # ── API Data حسب المنصة ───────────────────────────────────
    if platform == "shopify":
        result["shopify_api"] = scrape_shopify(base_url)
    elif platform in ("wordpress", "woocommerce"):
        result["wordpress_api"] = scrape_wordpress(base_url)

    # ── HTML Full Crawl ────────────────────────────────────────
    result["html_pages"] = full_crawl(base_url, args.max_pages, args.depth)

    # ── Summary ───────────────────────────────────────────────
    html_pages = result["html_pages"]
    result["summary"] = {
        "platform":        platform,
        "total_pages":     len(html_pages),
        "total_images":    sum(len(p.get("images", [])) for p in html_pages),
        "total_int_links": sum(len(p.get("internal_links", [])) for p in html_pages),
        "total_ext_links": sum(len(p.get("external_links", [])) for p in html_pages),
        "pages_with_schema": sum(1 for p in html_pages if p.get("schema_markup")),
        "pages_with_errors": sum(1 for p in html_pages if "error" in p),
        **({"shopify_products":    len(result.get("shopify_api", {}).get("products", []))} if platform == "shopify" else {}),
        **({"shopify_collections": len(result.get("shopify_api", {}).get("collections", []))} if platform == "shopify" else {}),
        **({"shopify_policies":    len(result.get("shopify_api", {}).get("policies", {}))} if platform == "shopify" else {}),
        **({"shopify_variants":    sum(len(p.get("variants",[])) for p in result.get("shopify_api",{}).get("products",[]))} if platform == "shopify" else {}),
        **({"shopify_prod_images": sum(len(p.get("images",[])) for p in result.get("shopify_api",{}).get("products",[]))} if platform == "shopify" else {}),
        **({"wp_posts":  len(result.get("wordpress_api", {}).get("posts", []))} if platform in ("wordpress","woocommerce") else {}),
    }

    # ── حفظ ───────────────────────────────────────────────────
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    export_csv(html_pages, out_csv)

    print("\n" + "═" * 60)
    print("  🏆  تم الانتهاء!")
    print(f"  📁  JSON : {out_json}")
    print(f"  📊  CSV  : {out_csv}.csv")
    print("═" * 60)
    print("  📊  الإحصائيات:")
    for k, v in result["summary"].items():
        print(f"     {k}: {v}")
    print()


if __name__ == "__main__":
    main()
