"""
Main script
"""
import asyncio, json

from src.loader import load_dzen_channels, load_model, dump_model
from src.utils import clean_articles
from src.models import ArticleDetail

from src.news_parser import DzenAggregator
from src.sender import Sender
from src.similarity import TextSimilarity


async def main():
    dzen_channels = load_dzen_channels()
    sim: TextSimilarity = load_model()
    
    dzen_aggregator = DzenAggregator(dzen_channels)
    sender = Sender()
    
    while True:
        # Would be nice to add ability to update channels on the fly,
        # like adding new entries into json file while script is running
        # but then we have to add this channel to DzenAggregator and
        # I already have been refactoring this project for 5 hours straight so...
        # Good night to myself (∪｡∪)｡｡｡zzz
        
        # Gather news
        articles: list(ArticleDetail) = []
        articles.extend(dzen_aggregator.get_dzen_news())
        # articles.extend(telegram_aggregator.get_telegram_news())
        
        if articles:
            # print(articles)
            # Remove old articles
            articles = sim.remove_duplicates(articles)
            
            # Send new articles (if they exist)
            await sender.send(articles)
        
            # Update and dump model with new articles
            sim.update(clean_articles(articles))
            dump_model(sim)


if __name__ == "__main__":
    asyncio.run(main())
