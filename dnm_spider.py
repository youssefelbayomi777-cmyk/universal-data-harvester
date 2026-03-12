import json
from urllib.parse import urljoin, urlparse
from scrapling.spiders import Spider, Response


class FullSiteCrawler(Spider):
    """
    زاحف شامل يسحب كل حاجة من الموقع:
    - كل الصفحات
    - كل المنتجات بكل تفاصيلها (اسم، سعر، وصف، صور، مقاسات، الوان)
    - كل النصوص
    - كل الروابط
    - كل الصور
    - الميتاداتا (SEO, Title, Description)
    - ملاحظات السياسات (Shipping, Refund)
    """
    name = "dnm_full_crawler"
    start_urls = ["https://dnmeg.com/"]
    
    # Only follow links within the same domain
    allowed_domains = ["dnmeg.com"]
    
    # Track visited URLs to avoid duplicates
    visited_urls = set()

    async def parse(self, response: Response):
        url = response.url

        # Skip already visited
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)

        # ── 1. Extract EVERYTHING from the current page ──────────────────────────

        # Meta data (SEO info)
        meta_title       = response.css('title::text').get("").strip()
        meta_description = response.css('meta[name="description"]::attr(content)').get("").strip()
        meta_og_title    = response.css('meta[property="og:title"]::attr(content)').get("").strip()
        meta_og_desc     = response.css('meta[property="og:description"]::attr(content)').get("").strip()
        meta_og_image    = response.css('meta[property="og:image"]::attr(content)').get("").strip()

        # All headings
        headings = {
            "h1": [h.strip() for h in response.css('h1::text').getall() if h.strip()],
            "h2": [h.strip() for h in response.css('h2::text').getall() if h.strip()],
            "h3": [h.strip() for h in response.css('h3::text').getall() if h.strip()],
            "h4": [h.strip() for h in response.css('h4::text').getall() if h.strip()],
        }

        # All text content (paragraphs, spans, li, td)
        all_texts = list(set([
            t.strip()
            for t in response.css('p::text, span::text, li::text, td::text, div::text, label::text').getall()
            if t.strip() and len(t.strip()) > 2
        ]))

        # All images on the page
        all_images = []
        for img_src in response.css('img::attr(src)').getall():
            if img_src:
                full_src = urljoin(url, img_src)
                if full_src.startswith('//'):
                    full_src = "https:" + full_src
                all_images.append(full_src)
        all_images = list(set(all_images))

        # All links on the page
        all_links = []
        for a_href in response.css('a::attr(href)').getall():
            if a_href:
                full_url = urljoin(url, a_href)
                all_links.append(full_url)
        all_links = list(set(all_links))

        # Navigation items
        nav_items = [
            {"text": a.css('::text').get("").strip(), "href": urljoin(url, a.attrib.get('href', ''))}
            for a in response.css('nav a, header a')
            if a.css('::text').get("").strip()
        ]

        # ── 2. Product-specific data (if this is a product page) ────────────────
        product_data = {}
        if "/products/" in url:
            price_regular = response.css('.price-item--regular::text').get("").strip()
            price_sale    = response.css('.price-item--sale::text').get("").strip()

            description_parts = (
                response.css('.product__description p::text').getall() or
                response.css('.product__description::text').getall() or
                response.css('.rte p::text').getall()
            )
            description = " ".join([d.strip() for d in description_parts if d.strip()])

            product_images = []
            for src in response.css('.product__media img::attr(src)').getall():
                if src:
                    product_images.append("https:" + src if src.startswith("//") else src)
            product_images = list(set(product_images))

            sizes  = [v.strip() for v in response.css('fieldset input::attr(value)').getall() if v.strip()]
            colors = [v.strip() for v in response.css('input[name="Color"]::attr(value)').getall() if v.strip()]

            washing_instructions = " ".join([
                t.strip()
                for t in response.css('.product__description li::text').getall()
                if t.strip()
            ])

            vendor  = response.css('.product__vendor::text').get("").strip()
            sku     = response.css('.product__sku::text').get("").strip()
            in_stock = not bool(response.css('button[disabled]').get())

            product_data = {
                "price_regular":        price_regular,
                "price_sale":           price_sale,
                "description":          description,
                "washing_instructions": washing_instructions,
                "product_images":       product_images,
                "sizes":                sizes,
                "colors":               colors,
                "vendor":               vendor,
                "sku":                  sku,
                "in_stock":             in_stock,
            }

        # ── 3. Policy / static page data ────────────────────────────────────────
        policy_data = {}
        if "/policies/" in url or "/pages/" in url:
            policy_text = " ".join([
                t.strip()
                for t in response.css('main p::text, main li::text, main h2::text, main h3::text').getall()
                if t.strip()
            ])
            policy_data = {"full_text": policy_text}

        # ── 4. Build the final scraped item ──────────────────────────────────────
        item = {
            "url":              url,
            "page_type":        (
                "product"    if "/products/" in url else
                "collection" if "/collections/" in url else
                "policy"     if "/policies/" in url else
                "page"       if "/pages/" in url else
                "home"
            ),
            "meta": {
                "title":       meta_title,
                "description": meta_description,
                "og_title":    meta_og_title,
                "og_desc":     meta_og_desc,
                "og_image":    meta_og_image,
            },
            "headings":        headings,
            "all_texts":       all_texts,
            "all_images":      all_images,
            "all_links":       all_links,
            "navigation":      nav_items,
        }

        if product_data:
            item["product_details"] = product_data
        if policy_data:
            item["policy_content"] = policy_data

        yield item

        # ── 5. Follow ALL internal links (to crawl the entire site) ─────────────
        for href in response.css('a::attr(href)').getall():
            if not href:
                continue
            full_url = urljoin(url, href)
            parsed   = urlparse(full_url)

            # Only follow links within the same domain, skip anchors/externals
            if (
                parsed.netloc in ("dnmeg.com", "www.dnmeg.com")
                and full_url not in self.visited_urls
                and not full_url.startswith("mailto:")
                and not full_url.startswith("tel:")
                and "#" not in full_url
                and "customer_authentication" not in full_url
                and "cdn.shopify" not in full_url
            ):
                yield response.follow(full_url, callback=self.parse)


# ── Run ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🕷️  بدأ كشط موقع DNM.EG بالكامل...")
    print("=" * 50)

    spider  = FullSiteCrawler()
    results = spider.start()

    # Save to JSON
    output_path = "dnm_FULL_SITE.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results.items, f, ensure_ascii=False, indent=4)

    print("=" * 50)
    print(f"✅  تم الانتهاء! تم كشط {len(results.items)} صفحة.")
    print(f"📁  تم حفظ البيانات في: d:/scripping/{output_path}")
