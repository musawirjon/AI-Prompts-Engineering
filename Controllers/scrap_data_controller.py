import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re

class ScrapDataController:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def clean_text(self, text: str) -> str:
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    def scrape_data(self, url: str) -> List[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'header', 'footer', 'nav']):
                element.decompose()

            # Extract text from different content elements
            content_elements = []
            
            # Get paragraphs
            paragraphs = soup.find_all('p')
            content_elements.extend([self.clean_text(p.get_text()) for p in paragraphs if len(p.get_text().strip()) > 50])
            
            # Get article content
            articles = soup.find_all(['article', 'main', 'section'])
            for article in articles:
                text = self.clean_text(article.get_text())
                if len(text) > 100:  # Only include substantial content
                    content_elements.append(text)
            
            # Get headings with their associated content
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings:
                heading_text = self.clean_text(heading.get_text())
                next_element = heading.find_next_sibling()
                if next_element and len(heading_text) > 0:
                    content = self.clean_text(next_element.get_text())
                    if len(content) > 50:
                        content_elements.append(f"{heading_text}: {content}")

            # Filter out duplicates and empty strings
            content_elements = list(filter(None, set(content_elements)))
            
            # Split long texts into smaller chunks (around 1000 characters)
            chunked_elements = []
            for text in content_elements:
                if len(text) > 1000:
                    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
                    chunked_elements.extend(chunks)
                else:
                    chunked_elements.append(text)

            return chunked_elements

        except requests.RequestException as e:
            print(f"Error scraping {url}: {str(e)}")
            return []
