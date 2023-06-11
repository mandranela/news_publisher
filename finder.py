import datetime
import time
from typing import List

from html_builder import HtmlPage
from driver_utils import Driver, SearchPage, ChannelPage
from parser import NewsScraper


class NewsChannel:
    """
    Класс для создания новостных каналов

    Атрибуты:
    name (str): название канала
    url (str): ссылка на источник новостей
    news (List): список новых новостей
    last_updated (datetime.datetime): время последнего обновления новостей на канале
    """

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.news = []
        self.last_updated = datetime.datetime.now()-datetime.timedelta(hours=1)

    def check_news(self):
        """
        Метод для проверки новостей на канале и уведомления подписчиков, если есть новые новости
        """
        self.news.clear()
        with Driver() as driver:
            channel_page = ChannelPage(
                driver=driver,
                channel_url=self.url
            )
            self.news = channel_page.get_channel(self.last_updated)

        self.last_updated = datetime.datetime.now()


class NewsAggregator:
    """
    Класс для агрегации новостей с нескольких каналов

    Атрибуты:
    channels (List): список объектов NewsChannel
    """

    def __init__(self, channels: List[NewsChannel]):
        self.channels = channels

    def run(self):
        """
        Метод для запуска агрегатора новостей
        """
        while True:
            for channel in self.channels:
                channel.check_news()

            for channel in self.channels:
                for news in channel.news:
                    with Driver() as driver:
                        search_page = SearchPage(
                            driver=driver,
                            query=news.title
                        )
                        links = search_page.get_links()
                        links.append(news.link)
                        news_scraper = NewsScraper(links)
                        articles = news_scraper.get_articles()
                        if len(articles) > 4:
                            HtmlPage.create(articles)
            time.sleep(400)
