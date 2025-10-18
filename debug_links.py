import sys
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def find_all_links(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            print(f"Text: {a_tag.text.strip()}, Href: {a_tag['href']}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_all_links(sys.argv[1])
    else:
        print("Please provide a URL as an argument.")
