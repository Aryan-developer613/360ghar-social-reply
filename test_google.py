import httpx
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlsplit

search_url = 'https://www.google.com/search'
params = {'q': 'site:reddit.com/r/ locality intelligence', 'num': 10}

try:
    with httpx.Client(
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        timeout=8.0,
        follow_redirects=True,
    ) as client:
        resp = client.get(search_url, params=params)
        resp.raise_for_status()
        print('HTTP Status:', resp.status_code)
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    count = 0
    for a_tag in soup.select('a[href]'):
        href = a_tag.get('href', '')
        if 'reddit.com' in href:
            print('Found raw URL:', href)
        if href.startswith('/url?'):
            qs = parse_qs(urlsplit(href).query)
            actual_urls = qs.get('q', [])
            if actual_urls:
                href = actual_urls[0]
                if 'reddit.com' in href:
                    print('Found parsed URL:', href)
                    count += 1
    print('Total Reddit URLs found:', count)
except Exception as e:
    print('Exception:', e)
