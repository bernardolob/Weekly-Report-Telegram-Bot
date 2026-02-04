import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application
from typing import Final
from sheetsReader import refresh_cache, getTWILResponsible
import logging

logging.basicConfig(
    filename="logs/telegrambot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


SECOND_WARNING_MESSAGE: str = """
🚨 #WeeklyReport last call!
⏳ Few hours left!
💡 TWIL Reminder: {twil_responsible}
🔗 Link: https://forms.gle/XkYLXHCKF9HEur6s9
"""


# WHITELIST: list[int] = [-1001279975882, -5068062676]
WHITELIST: list[int] = [-1001279975882]
# WHITELIST: list[int] = [-5068062676]


TOKEN: Final = '8084223298:AAF0bnTCct6D99FPHul1ezTse5cS7jLQFsM'
BOT_USERNAME: Final = '@saobernardo_bot'

################################ MAIN ################################


async def main():
    logging.info("-----------")
    logging.info("Starting one-shot bot...")
    app = Application.builder().token(TOKEN).build()

    await app.initialize()
    await app.bot.initialize()

    logging.info(datetime.now())
    logging.info("Second warning message request.")

    await refresh_cache()
    twil = await getTWILResponsible()

    for chat_id in WHITELIST:
        await app.bot.send_message(
            chat_id=chat_id,
            text=SECOND_WARNING_MESSAGE.format(twil_responsible=twil),
            disable_web_page_preview=True,
        )

    logging.info("Messages sent. Shutting down.")
    await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
