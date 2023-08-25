"""
Handles operations with selenium (emulating browser)
"""
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service

from src.models import Article
from src.utils import parse_time_string


class Driver:
    """
    Класс для создания и использования единственного
    экземпляра веб-драйвера.
    """

    def __init__(self):
        options = Options()
        service = Service(executable_path=r'C:\\Users\\MANDR\Downloads\\geckodriver.exe',)
        options.add_argument('-headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Firefox(service=service, options=options)

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


class BasePage:
    """
    Базовый класс для страниц веб-сайта.
    """

    def __init__(self, driver: webdriver.Firefox):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def get_page_html(self) -> str:
        """
        Получает и возвращает HTML-код страницы.
        """
        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )
        return self.driver.page_source

    def scroll_down(self) -> None:
        """
        Прокручивает страницу вниз.
        """
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(1)


class SearchPage(BasePage):
    """
    Класс для страницы поиска на Dzen.
    """

    url = "https://m.dzen.ru/search"
    max_scrolls = 3

    def __init__(self, driver: webdriver.Firefox, query: str):
        """
        Инициализирует класс SearchPage.

        :param driver: экземпляр веб-драйвера.
        :param query: строка запроса для поиска.
        """
        super().__init__(driver)
        self.query = query

        self.url_new = f"{self.url}?query={self.query}"

    def get_links(self) -> list[str]:
        """
        Получает и возвращает список ссылок на статьи,
        найденные по запросу.

        :return: список ссылок на статьи.
        """
        links = []
        self.driver.get(self.url_new)
        for _ in range(self.max_scrolls):
            self.scroll_down()
            page_html = self.get_page_html()
            soup = BeautifulSoup(page_html, 'html.parser')
            links = [p['href'].split('?')[0] for p in soup.select(
                'a.card-image-compact-view__clickable:nth-of-type(odd)'
            )]
            links = links[1::2]
            if len(links) > 3:
                return links[:4]
        return links[:4]


class ChannelPage(BasePage):
    """
    Класс для страницы канала на Dzen.
    """

    max_scrolls = 5

    def __init__(self, driver: webdriver.Firefox, channel_url: str):
        """
        Инициализирует класс ChannelPage.

        :param driver: экземпляр веб-драйвера.
        :param channel_url: URL канала.
        """
        super().__init__(driver)
        self.channel_url = channel_url

    def get_channel(self, last_update) -> list[Article]:
        articles = []
        self.driver.get(self.channel_url)
        for _ in range(self.max_scrolls):
            self.scroll_down()
            page_html = self.get_page_html()
            soup = BeautifulSoup(page_html, 'html.parser')
            _articles = soup.find_all('div', {'class': 'card-image-compact-view__content'})
            if parse_time_string(_articles[-1].find('div', {'class': 'zen-ui-common-layer-meta'}).text) < last_update:
                break

        page_html = self.get_page_html()
        soup = BeautifulSoup(page_html, 'html.parser')
        _articles = soup.find_all('div', {'class': 'card-image-compact-view__content'})
        for _article in _articles:
            published_time = parse_time_string(_article.find('div', {'class': 'zen-ui-common-layer-meta'}).text)
            title = _article.h2.text
            link = _article.find('a', {'class': 'zen-ui-line-clamp'})['href'].split('?')[0]
            if published_time > last_update:
                articles.append(Article(title=title, published_time=published_time, link=link))
        return articles


class ArticlePage(BasePage):
    """
    Класс для страницы статьи на Dzen.
    """
    def __init__(self, driver: webdriver.Firefox, article_url: str):
        """
        Инициализирует класс ArticlePage.

        :param driver: экземпляр веб-драйвера.
        :param article_url: URL статьи.
        """
        super().__init__(driver)
        self.article_url = article_url

    def get_article(self) -> str:
        self.driver.get(self.article_url)

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "article")))
        page_html = self.get_page_html()
        
        return page_html
