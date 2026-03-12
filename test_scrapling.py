from scrapling.fetchers import StealthyFetcher

def test():
    print("Testing Scrapling...")
    # Using a simple URL
    url = "https://quotes.toscrape.com"
    print(f"Fetching {url} with StealthyFetcher...")
    try:
        page = StealthyFetcher.fetch(url)
        print(f"Status: {page.status}")
        quotes = page.css(".quote")
        print(f"Found {len(quotes)} quotes.")
        if quotes:
            print(f"First quote: {quotes[0].css('.text::text').get()}")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Let's see what attributes it has if it fails
        if 'page' in locals():
            print(f"Available attributes: {[a for a in dir(page) if not a.startswith('_')]}")

if __name__ == "__main__":
    test()
