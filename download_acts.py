
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Create a directory to store the legal acts
if not os.path.exists("akty_prawne"):
    os.makedirs("akty_prawne")

# List of URLs from lawmap-front.mmd
urls = [
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU19970780483",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20120001169",
    "https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX%3A32019L0882",
    "https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX%3A32016L2102",
    "https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32006R1107",
    "https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX%3A32011R0181",
    "https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX%3A12007P000",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU19640160093",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20011381545",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20110210112",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20190002019",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20020730050",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU19940770067",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20041670710",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20190001696",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20190000848",
    "https://isap.sejm.gov.pl/isap.nsf/download.xsp/WDU20240000731/T/D20240731L.pdf",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20020750690",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20230001054",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20140000441",
    "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20110001509"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_isap_pdf_url(page_url):
    """Finds the PDF link on an ISAP page."""
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Prefer "Tekst ujednolicony"
        pdf_link_tag = soup.find('a', string=re.compile(r'Tekst ujednolicony'))
        if pdf_link_tag:
            pdf_link = pdf_link_tag.find_next('a')
        else:
            # Fallback to "Tekst ogłoszony"
            pdf_link_tag = soup.find('a', string=re.compile(r'Tekst ogłoszony'))
            if pdf_link_tag:
                pdf_link = pdf_link_tag.find_next('a')
            else:
                pdf_link = None

        if pdf_link and pdf_link.has_attr('href'):
            return urljoin('https://isap.sejm.gov.pl', pdf_link['href'])
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {page_url}: {e}")
    return None

def get_eurlex_pdf_url(page_url):
    """Finds the PDF link on a EUR-Lex page."""
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = soup.find('a', title=re.compile(r"Pokaż wersję PDF tego dokumentu"))
        if pdf_link and pdf_link.has_attr('href'):
            return urljoin(page_url, pdf_link['href'])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {page_url}: {e}")
    return None

def download_pdf(pdf_url, filename):
    """Downloads a PDF from a URL and saves it."""
    try:
        response = requests.get(pdf_url, headers=headers, stream=True)
        response.raise_for_status()
        filepath = os.path.join("akty_prawne", filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {pdf_url}: {e}")

def main():
    for url in urls:
        filename = ""
        pdf_url = None

        if url.endswith('.pdf'):
            pdf_url = url
            filename = url.split('/')[-1]
        elif "isap.sejm.gov.pl" in url:
            pdf_url = get_isap_pdf_url(url)
            match = re.search(r'id=(WDU\w+)', url)
            if match:
                filename = f"{match.group(1)}.pdf"
        elif "eur-lex.europa.eu" in url:
            pdf_url = get_eurlex_pdf_url(url)
            match = re.search(r'uri=CELEX%3A(\w+)', url)
            if match:
                filename = f"CELEX_{match.group(1)}.pdf"

        if pdf_url and filename:
            download_pdf(pdf_url, filename)
        else:
            print(f"Could not find PDF for {url}")

if __name__ == "__main__":
    main()
