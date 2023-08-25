"""
Handles operations with writing/reading files
"""
import os, json, pickle
from pathlib import Path

from src.utils import time_counter
from src.news_parser import NewsChannel
from src.similarity import TextSimilarity

DEFAULT_DZEN_CHANNELS_PATH = "./dzen_channels.json"
DEFAULT_MODEL_PATH = "./dump_TextSimilarity.pkl"
DEFAULT_NEWS_PATH = "./src/default_news.txt"

@time_counter(start_message="Model dumping started.", finish_message="Model dumping finished.")
def dump_model(model, path: str = DEFAULT_MODEL_PATH) -> TextSimilarity:
    # Dump the model
    filename = Path(path)
    filename.touch(exist_ok=True)
    
    with open(path, 'wb+') as file:
        pickle.dump(model, file, -1)

@time_counter(start_message="Model loading started.", finish_message="Model loading finished.")
def load_model(path: str = DEFAULT_MODEL_PATH) -> TextSimilarity:
    try:
        with open(path, 'rb') as file:
            model = pickle.load(file)
            return model
    except Exception:
        sim: TextSimilarity = TextSimilarity()
        with open(DEFAULT_NEWS_PATH, 'r', encoding='utf-8') as file:
            news = file.readlines()
            sim.train(news)
        return sim

def load_dzen_channels(path: str = DEFAULT_DZEN_CHANNELS_PATH):
    with open(path) as file:
        dzen_channels = json.load(file)
    
    dzen_channels = [NewsChannel(name, url) for name, url in dzen_channels.items()]
    
    return dzen_channels
