"""
Handles operations with text similarity / checking for posted news
"""
from gensim import corpora, models, similarities

from src.models import ArticleDetail
from src.utils import clean_paragraphs, time_counter


class TextSimilarity:
    def __init__(self):
        """
        Инициализирует объект модели сходства текста.

        Атрибуты:
        documents (list): Список документов для обучения модели.
        dictionary (gensim.corpora.Dictionary): Словарь, содержащий уникальные токены из обучающих документов.
        corpus (list): Корпус, содержащий представление документов в виде мешка слов.
        tfidf (gensim.models.TfidfModel): Модель TF-IDF для преобразования корпуса.
        index (gensim.similarities.Similarity): Индекс для быстрого поиска сходства между документами.
        """
        self.threshold = 0.2

        self.documents = []
        self.dictionary = None
        self.corpus = None
        self.tfidf = None
        self.index = None

    def train(self, documents: list[str]) -> None:
        """
        Обучает модель на основе списка документов.

        :param: documents (list[str]): Список документов для обучения модели.

        :returns: None
        """
        
        self.documents = documents
        processed_docs = [doc.lower().split() for doc in documents]
        self.dictionary = corpora.Dictionary(processed_docs)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in processed_docs]
        self.tfidf = models.TfidfModel(self.corpus)
        corpus_tfidf = self.tfidf[self.corpus]
        self.index = similarities.Similarity(None, corpus_tfidf, num_features=len(self.dictionary))

    @time_counter(start_message="Updating model started.", finish_message="Updating model finished.")
    def update(self, documents: list[str]) -> None:
        """
        Обновляет модель, добавляя новые строки.

        :param: new_string (list[str]): Новые строки для добавления в модель.

        :returns: None
        """
        self.documents.extend(documents)
        processed_docs = [doc.lower().split() for doc in documents]
        self.dictionary.add_documents(processed_docs)
        self.corpus.extend(self.dictionary.doc2bow(processed_docs))
        self.tfidf = models.TfidfModel(self.corpus)
        corpus_tfidf = self.tfidf[self.corpus]
        self.index = similarities.Similarity(None, corpus_tfidf, num_features=len(self.dictionary))

    def get_similarity_values(self, query: str) -> list[float]:
        """
        Возвращает значения сходства для заданного запроса.

        :param: query (str): Запрос для получения значений сходства.

        :returns: similarity_values (list[float]): Список значений сходства для заданного запроса.
        """
        query_bow = self.dictionary.doc2bow(query.lower().split())
        query_tfidf = self.tfidf[query_bow]
        sims = self.index[query_tfidf]
        similarity_values = [*sims]
        return similarity_values

    def get_similar_document_indexes(self, query: str) -> list[int]:
        """
        Возвращает индексы документов, сходство с которыми превышает пороговое значение.

        :param: query (str): Запрос для поиска похожих документов.

        :returns: indexes (list[str]): Список индексов документов с сходством, превышающим пороговое значение.
        """
        similarity_values = self.get_similarity_values(query)
        similar_indexes = [i for i, sim in enumerate(similarity_values) if sim >= self.threshold]
        # print(similar_indexes, "\n", similarity_values)
        return similar_indexes
    
    def is_unique(self, query: str) -> bool:
        """
        Проверяет, является ли заданный запрос уникальным.

        :param: query (str): Запрос для проверки уникальности.

        :returns: is_unique (bool): True, если запрос уникален, иначе False.
        """
        similar_indexes = self.get_similar_document_indexes(query)
        is_unique = len(similar_indexes) == 0   # there is zero similar texts 
        return is_unique
    
    @time_counter(start_message="Removing dublicates started.", finish_message="Removing dublicates finished.")
    def remove_duplicates(self, articles: list[ArticleDetail]) -> list[ArticleDetail]:
        """
        Удаляет из списка новостей те, что вероятно уже были опубликованы
        """
        initial_size = len(articles)
        
        articles = [article for article in articles if self.is_unique(clean_paragraphs(article.paragraphs))]
        
        print(f"Removed {initial_size - len(articles)} articles.", end=" ")
        
        return articles
