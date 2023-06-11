import time
from typing import List

import requests
from bs4 import BeautifulSoup

from models import ArticleDetail


class NewsScraper:
    def __init__(self, urls: List[str]):
        self.urls = urls

    def get_articles(self) -> List[ArticleDetail]:
        articles = []
        for url in self.urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            article = soup.find("article")
            try:
                photo_url = article.find('img')['src']
            except:
                photo_url = None
            title = article.h1.text
            paragraphs = [p.text for p in article.find_all("p")]
            articles.append(ArticleDetail(title=title, paragraphs=paragraphs, photo_url=photo_url))
            time.sleep(1)
        return articles
