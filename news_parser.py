import time
from typing import List

import requests
from bs4 import BeautifulSoup

from models import ArticleDetail
from driver_utils import ArticlePage

class NewsScraper:
    def __init__(self, urls: List[str]):
        self.urls = urls

    def get_articles(self, driver) -> List[ArticleDetail]:
        articles = []
        for url in self.urls:
            article_page = ArticlePage(driver, url)
            html_page = article_page.get_article()
            # response = requests.get(url) <- don't work, dzen added redirect 
            soup = BeautifulSoup(html_page, "html.parser")
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
