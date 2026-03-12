from scrapling.fetchers import Fetcher
try:
    print("Testing connection to aaro.mil...")
    page = Fetcher.get("https://www.aaro.mil", stealthy_headers=True)
    print(f"Status Code: {page.status}")
    print(f"Title: {page.css('title::text').get()}")
except Exception as e:
    print(f"Error: {e}")
