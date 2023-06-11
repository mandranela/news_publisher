from finder import NewsAggregator, NewsChannel

if __name__ == '__main__':
    channels = [
        NewsChannel('AIF', 'https://dzen.ru/aif.ru'),
        NewsChannel('RBC', 'https://dzen.ru/rbc.ru'),
        NewsChannel('KPRU', 'https://dzen.ru/kpru'),
        NewsChannel('Lenta.ru', 'https://dzen.ru/lenta.ru'),
        NewsChannel('TopWar.ru', 'https://dzen.ru/topwar.ru'),
    ]
    aggregator = NewsAggregator(channels)
    aggregator.run()
