import requests
from bs4 import BeautifulSoup
class ScrapDataController():
    def __init__(self):
        pass
    def scrape_data(selft, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from paragraphs, you can customize this part to extract other elements
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        
        return text
