"""
Handles operations with gathering news from dzen
"""
import datetime

from bs4 import BeautifulSoup

from src.models import Article, ArticleDetail
from src.driver_utils import Driver, ChannelPage, ArticlePage
from src.utils import time_counter


class NewsChannel:
    """
    Класс для создания новостных каналов

    Атрибуты:
    name (str): название канала
    url (str): ссылка на источник новостей
    news (list): список новых новостей
    last_updated (datetime.datetime): время последнего обновления новостей на канале
    """

    def __init__(self, name: str, url: str):
        self.name: str = name
        self.url: str = url
        self.news: list[Article] = []
        self.last_updated: datetime = datetime.datetime.now()-datetime.timedelta(minutes=20)
        
    def check_news(self):
        """
        Метод для проверки новостей на канале и уведомления подписчиков, если есть новые новости
        """
        self.news.clear()
        with Driver() as driver:
            channel_page = ChannelPage(driver=driver, channel_url=self.url)
            self.news = channel_page.get_channel(self.last_updated)

        self.last_updated = datetime.datetime.now()


class DzenAggregator:
    """
    Класс для агрегации новостей с нескольких каналов Дзен

    Атрибуты:
    channels (list): список объектов NewsChannel
    """

    def __init__(self, channels: list[NewsChannel]):
        self.channels: list[NewsChannel] = channels

    @time_counter(start_message=f"Updating news started.", finish_message="Updating news finished.")
    def update_news_channels(self):
        for channel in self.channels:
            channel.check_news()
    
    def get_dzen_news(self) -> list[ArticleDetail]:
        """
        Метод для сбора новостей с Дзена
        """
        self.update_news_channels()
        
        articles: list[ArticleDetail] = []
        links: list[str] = [news.link for channel in self.channels for news in channel.news]
        if links:
            news_scraper = NewsScraper(links)
            articles.extend(news_scraper.get_articles())
        else:
            print("No articles found in channels.")

        return articles


class NewsScraper:
    def __init__(self, urls: list[str]):
        self.urls = urls

    @time_counter(start_message="Articles gathering started.", finish_message="Articles gathering finished.")
    def get_articles(self) -> list[ArticleDetail]:
        articles = []
        for url in self.urls:
            # response = requests.get(url) <- don't work, dzen added redirect 
            with Driver() as driver:
                article_page = ArticlePage(driver, url)
                html_page = article_page.get_article()
            soup = BeautifulSoup(html_page, "html.parser")
            article = soup.find("article")
            try:
                photo_url = article.find('img')['src']
            except:
                photo_url = None
            title = article.h1.text
            paragraphs = [p.text for p in article.find_all("p")]
            articles.append(ArticleDetail(title=title, paragraphs=paragraphs, photo_url=photo_url))
        return articles
