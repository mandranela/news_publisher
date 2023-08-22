import asyncio, json

from finder import NewsAggregator, NewsChannel


def load_dzen_channels(path: str):
    with open(path) as file:
        dzen_channels = json.load(file)
    
    dzen_channels = [NewsChannel(name, url) for name, url in dzen_channels.items()]
    
    return dzen_channels


async def main():
    dzen_path = "dzen_channels.json"
    
    channels = load_dzen_channels(dzen_path)
    aggregator = NewsAggregator(channels)
    await aggregator.run()


if __name__ == "__main__":
    asyncio.run(main())
