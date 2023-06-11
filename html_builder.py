import base64
import uuid
from typing import List

import requests
import urllib3
from models import ArticleDetail
from settings import USER, SITENAME, PASSWORD

# Отключаем проверку сертификата
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sitename = SITENAME
url = f'{sitename}/wp-json/wp/v2/posts'
media_url = f'{sitename}/wp-json/wp/v2/media'
user = USER
password = PASSWORD
creds = f'{user}:{password}'
token = base64.b64encode(creds.encode())


class HtmlPage:
    @staticmethod
    def create(news: List[ArticleDetail]):
        photo_url = ''
        photo_url_2 = ''
        _photo_url_2 = ''
        photos = []
        for _news in news:
            if _news.photo_url is not None and _news.photo_url != '':
                photos.append(_news.photo_url)

        if len(photos) > 1:
            photo_url = photos[0]

        _photo_url, _idx = get_photo_link(photo_url)

        if len(photos) > 2:
            photo_url_2 = photos[1]
            _photo_url_2, _idx_2 = get_photo_link(photo_url_2)

        title = news[0].title
        texts = HtmlPage.create_texts(news, _photo_url_2)
        page = HtmlPage.build_page(title, _photo_url, texts)
        HtmlPage.post_wp(title, page, _idx)

    @staticmethod
    def create_texts(news: List[ArticleDetail], photo_url):
        texts_html = ''
        for i, n in enumerate(news):
            text_html = ''
            if i == 2:
                text_html += f'<img src = "{photo_url}">'
            if i != 0:
                text_html += f'\n<h3>{n.title}</h3>'
            for p in n.paragraphs:
                text_html += f'\n<p>{p}</p>'
            texts_html += text_html
        return texts_html

    @staticmethod
    def build_page(title, photo_url, texts):
        page = f"""
        {texts}
        """
        return page

    @staticmethod
    def post_wp(title, page, idx):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token.decode('utf-8')
        }

        data = {
            'title': title,
            'content': page,
            'status': 'publish',
            'featured_media': idx,
        }
        res = requests.post(url, headers=headers, json=data)


def load_photo_wp(data, filename):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'image/jpg',
        'Content-Disposition': 'attachment; filename=%s' % filename
    }
    res = requests.post(
        url=media_url,
        data=data,
        headers=headers,
        auth=(user, password),
        verify=False
    )
    res = res.json()
    link = res.get('guid').get("rendered")
    idx = res.get('id')
    return link, idx


def get_photo_link(image_url):
    idx = ''
    if image_url == '':
        return '', ''
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = response.content
        file_name = str(uuid.uuid4()) + '.png'
        try:
            link, idx = load_photo_wp(image_data, file_name)
        except:
            link = image_url
    else:
        link = image_url
    return link, idx
