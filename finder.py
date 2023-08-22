import datetime
import time
from typing import List

from models import ArticleDetail
from sender import Sender
from driver_utils import Driver, SearchPage, ChannelPage
from news_parser import NewsScraper

from bito import Bito


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
        self.last_updated = datetime.datetime.now()-datetime.timedelta(minutes=20)

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
        self.sender = Sender()

    async def run(self):
        """
        Метод для запуска агрегатора новостей
        """
        while True:
            time_n = time.time()
            print("Check news started.", end=" ", flush=True)
            for channel in self.channels:
                channel.check_news()
            print("Check news finished. Time: ", time.time() - time_n)

            for channel in self.channels:
                # print(channel.news)
                for news in channel.news:
                    with Driver() as driver:
                        search_page = SearchPage(
                            driver=driver,
                            query=news.title
                        )
                        
                        time_l = time.time()
                        print("Links gathering started.", end=" ", flush=True)
                        links = search_page.get_links()
                        links.append(news.link)
                        print("Links gathering finished. Time: ", time.time() - time_l)
                        
                        time_a = time.time()
                        print("Articles gathering started.", end=" ", flush=True)
                        news_scraper = NewsScraper(links)
                        articles = news_scraper.get_articles(driver)
                        print("Articles gathering finished. Time: ", time.time() - time_a)

                        time_b = time.time()
                        print("Shrinkng news started.", end=" ", flush=True)
                        bito = Bito()
                        articles = [
                            ArticleDetail(
                                title=article.title, 
                                paragraphs=[bito.shrink_news("\n".join(article.paragraphs))], 
                                photo_url=article.photo_url)
                                    for article in articles
                                    ]
                        print("Shrinking news finished. Time: ", time.time() - time_b)

                        time_s = time.time()
                        print("Sending news started.", end=" ", flush=True)
                        await self.sender.send(articles)
                        print("Sending news finished. Time: ", time.time() - time_s)
                        
            time.sleep(1)
