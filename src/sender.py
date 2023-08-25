"""
Handles operations with sending news via telegram
"""
import telegram

from src.models import ArticleDetail
import asyncio


class Sender(object):
    def __init__(self):
        self.token = "6551139063:AAGuHDXHwSMqizMSv97VoSQtZEAxQgi7mNA"
        self.target_chat_id = "829315506"

        self.bot = telegram.Bot(token=self.token)
    
    
    def refactor_paragraphs(self, paragraphs: list[str]) -> list[str]:
        """
        Refactor paragraphs to lower their number, 
        while keeping the size of each one of them 
        lower than telegram message limit -4096.
        """
        max_length = 4096
        result = []
        current_paragraph = paragraphs[0]

        for paragraph in paragraphs[1:]:
            if len(current_paragraph) + len(paragraph) + 1 <= max_length:
                current_paragraph += "\n" + paragraph
            else:
                result.append(current_paragraph)
                current_paragraph = paragraph

        result.append(current_paragraph)
        return result


    async def send(self, articles: list[ArticleDetail]) -> None:
        """
        Sends articles in chat with target_chat_id.
        """
        error_num = 0
        for article in articles:
            try:
                message = f"{article.title}\n"
                if article.photo_url:
                    if sum(len(paragrph) for paragrph in article.paragraphs) < 1024:
                        message += "\n".join(f"{paragraph}" for paragraph in article.paragraphs)
                        await self.bot.send_photo(chat_id=self.target_chat_id, photo=article.photo_url, caption=message)
                    else:
                        await self.bot.send_photo(chat_id=self.target_chat_id, photo=article.photo_url, caption=message)
                        paragraphs = self.refactor_paragraphs(article.paragraphs)
                        for paragraph in paragraphs:
                            message = paragraph
                            await self.bot.send_message(chat_id=self.target_chat_id, text=message)
                else:
                    if sum(len(paragrph) for paragrph in article.paragraphs) < 4096:
                        message += "\n".join(f"{paragraph}" for paragraph in article.paragraphs)
                        await self.bot.send_message(chat_id=self.target_chat_id, text=message)
                    else:
                        paragraphs = self.refactor_paragraphs(article.paragraphs)
                        for paragraph in paragraphs:
                            message = paragraph
                            await self.bot.send_message(chat_id=self.target_chat_id, text=message)     
            except Exception as e:
                print("Exception:", e)
                error_num += 1
        print("Sent:", len(articles) - error_num)


if __name__ == "__main__":
    sender = Sender()
    article = ArticleDetail(
        title="Title",
        paragraphs=["Paragraph number one: what the hell???\nNOWAYING", 
                    "Paragraph number two: eat well and sleep forever"],
        photo_url=None
    )
    
    asyncio.run(sender.send(articles=[article]))