import requests
from bs4 import BeautifulSoup
from langdetect import detect
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor  # Fixed: Added import
import time
import random

# Configuration
MAX_WORKERS = 10  # Safe for most servers
TIMEOUT = 5
REQUEST_DELAY = 0.2  # Seconds between batches (avoid bans)

def get_sitemap_urls(sitemap_url):
    """Extract all URLs from sitemap.xml"""
    try:
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.text, 'lxml-xml')
        return [loc.text.strip() for loc in soup.find_all('loc')]
    except Exception as e:
        print(f"Sitemap error: {e}")
        return []

def detect_language(url):
    """Detect page language with error handling"""
    try:
        time.sleep(REQUEST_DELAY * random.uniform(0.5, 1.5))  # Random delay
        response = requests.get(url, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join(soup.stripped_strings)[:1000]  # Cleaner text extraction
        return (url, detect(text))
    except Exception as e:
        return (url, f"Error: {str(e)}")

def analyze_languages(urls):
    """Process URLs with threading and save results"""
    language_counts = defaultdict(int)
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(detect_language, url) for url in urls]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):  # Fixed: Added 'concurrent.'
            url, lang = future.result()
            results.append((url, lang))
            language_counts[lang] += 1
            
            # Progress tracking
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{len(urls)} | Last language: {lang}")

    return results, dict(language_counts)

if __name__ == "__main__":
    # Step 1: Load URLs
    sitemap_url = "" # Update
    urls = get_sitemap_urls(sitemap_url)[:10]  # First 5000 for testing
    print(f"Loaded {len(urls)} URLs")

    # Step 2: Run analysis
    start_time = time.time()
    url_languages, language_counts = analyze_languages(urls)
    
    # Step 3: Save results
    with open("language_results.csv", "w") as f:
        f.write("URL,Language\n")
        for url, lang in url_languages:
            f.write(f"{url},{lang}\n")
    
    print("\n=== Language Summary ===")
    for lang, count in sorted(language_counts.items(), key=lambda x: -x[1]):
        print(f"{lang}: {count}")
    
    print(f"\nCompleted in {(time.time() - start_time) / 60:.1f} minutes")
