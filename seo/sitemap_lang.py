# Check for pages in sitemap with page content not in Japanese

import requests
from bs4 import BeautifulSoup
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import random

# Configuration
MAX_WORKERS = 10
TIMEOUT = 5
REQUEST_DELAY = 0.2  # Delay between threads (multiplied by a random factor)

session = requests.Session()
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)


def get_sitemap_urls(sitemap_url):
    """Extract all urls from sitemap.xml"""
    try:
        response = session.get(sitemap_url, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'lxml-xml')
        return [loc.text.strip() for loc in soup.find_all('loc')]
    except Exception as e:
        print(f"Sitemap error: {e}")
        return []

def extract_visible_text(soup):
    """Extract meaningful text from the page, ignoring nav/boilerplate"""
    main_content = soup.find('main') or soup.find('article')
    if main_content:
        elements = main_content.find_all(['p', 'li', 'h1', 'h2', 'h3'])
    else:
        elements = soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'article'])

    text = ' '.join(el.get_text(strip=True) for el in elements)
    return text[:1000]  # Truncate for speed and consistency


def detect_language(url):
    """Detect the main content language of the page"""
    try:
        time.sleep(REQUEST_DELAY * random.uniform(0.5, 1.5))  # Random delay to be polite
        response = session.get(url, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')

        text = extract_visible_text(soup)

        if not text.strip():
            return (url, "no_text")

        try:
            lang = detect(text)
        except LangDetectException:
            lang = "undetected"

        return (url, lang)
    except Exception as e:
        return (url, f"Error: {str(e)}")


def analyze_languages(urls):
    """Analyze a list of urls for language detection using threads"""
    language_groups = defaultdict(list) 

    # Randomly shuffle urls before processing
    random.shuffle(urls)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(detect_language, url) for url in urls]

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            url, lang = future.result()
            language_groups[lang].append(url)

            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(urls)} | Last: {url} → {lang}")

    return language_groups

if __name__ == "__main__":
    sitemap_url = "" # Update
    urls = get_sitemap_urls(sitemap_url)
    print(f"Loaded {len(urls)} URLs from sitemap.")

    # Random sample (remove to check all urls)
    sampled_urls = random.sample(urls, min(200, len(urls))) 

    start_time = time.time()
    language_groups = analyze_languages(sampled_urls)

    # Print urls that are not in japanese
    print("\n=== URLs Not in Japanese ===")
    for lang, urls_in_lang in language_groups.items():
        if lang != 'ja':
            print(f"\n{lang} ({len(urls_in_lang)} URLs):")
            for url in urls_in_lang:
                print(f"  - {url}")

    print(f"\nCompleted in {(time.time() - start_time) / 60:.1f} minutes")
