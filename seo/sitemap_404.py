# Check for pages in sitemap with 404 errors

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import random
from collections import deque
import threading

# Configuration
MAX_WORKERS = 5
TIMEOUT = 5
MAX_RETRIES = 2
SITEMAP_URL = "" # Update

# Thread-safe print
print_lock = threading.Lock()
def safe_print(message):
    with print_lock:
        print(message)

def get_sitemap_urls(sitemap_url):
    """Extract and shuffle URLs from sitemap.xml"""
    try:
        response = requests.get(sitemap_url, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'xml')
        urls = [loc.text.strip() for loc in soup.find_all('loc')]
        random.shuffle(urls)  # Shuffle URLs
        return urls
    except Exception as e:
        safe_print(f"sitemap error: {e}")
        return []

def check_url(url):
    """Check URL with retries and real-time output"""
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.head(
                url, 
                timeout=TIMEOUT, 
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if response.status_code == 404:
                safe_print(f"404 found: {url}")
            return
        except requests.exceptions.Timeout:
            if attempt == MAX_RETRIES:
                pass 
        except requests.exceptions.RequestException:
            if attempt == MAX_RETRIES:
                pass 
        time.sleep(1)

if __name__ == "__main__":
    safe_print(f"checking urls in: {SITEMAP_URL}")
    
    urls = get_sitemap_urls(SITEMAP_URL)
    if not urls:
        safe_print("no urls found in sitemap")
        exit()

    safe_print(f"found {len(urls)} urls. checking for 404s...\n")
    
    # Process URLs with thread pool
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for url in urls:
            future = executor.submit(check_url, url)
            futures.append(future)
        
        # Wait for all tasks to complete
        for future in futures:
            future.result()

    safe_print("\nscan complete. 404 errors shown if found.")
