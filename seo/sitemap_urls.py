import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urlparse

def analyze_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml-xml')
        urls = [loc.text.strip() for loc in soup.find_all('loc')]
        subdir_counts = defaultdict(int)
        
        for url in urls:
            parsed_url = urlparse(url)
            path = parsed_url.path
            parts = [p for p in path.split('/') if p]
            if len(parts) >= 2:
                subdir = f"/{parts[1]}/"
                subdir_counts[subdir] += 1

        print(f"Total URLs: {len(urls)}")
        print(f"Unique subdirectories: {len(subdir_counts)}")
        print("\nURL count by subdirectory:")
        
        for subdir, count in sorted(subdir_counts.items(), key=lambda x: -x[1]):
            print(f"{subdir}: {count} URLs")
        
        return subdir_counts
    
    except Exception as e:
        print(f"Error: {e}")
        return None

sitemap_url = "" # Update
analyze_sitemap(sitemap_url)
