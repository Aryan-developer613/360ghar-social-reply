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
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    for a_tag in soup.select('a[href]'):
        href = a_tag.get('href', '')
        if 'reddit.com' in href:
            print('Found raw URL:', href)
            h3 = a_tag.find('h3')
            title = h3.text if h3 else 'NO TITLE'
            print('Title:', title)
except Exception as e:
    print('Exception:', e)
