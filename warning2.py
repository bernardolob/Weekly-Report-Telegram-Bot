import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application
from typing import Final
from sheetsReader import refresh_cache, getTWILResponsible
import logging
import os
from dotenv import load_dotenv

# Carrega variáveis do ficheiro .env para o ambiente
load_dotenv()


logging.basicConfig(
    filename="logs/telegrambot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


SECOND_WARNING_MESSAGE: str = """
🚨 #WeeklyReport last call!
⏳ Few hours left!
💡 TWIL Reminder: {twil_responsible}
🔗 Link: {forms_link}
"""

WHITELIST: list[int] = [
    int(chat_id.strip())
    for chat_id in os.getenv("TELEGRAM_WHITELIST", "").split(",")
    if chat_id.strip()
]

TOKEN: Final = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError(
        "TELEGRAM_TOKEN não definido. Cria um ficheiro .env (ver .env.example) "
        "com a variável TELEGRAM_TOKEN=..."
    )

BOT_USERNAME: Final = os.getenv("BOT_USERNAME")
if not BOT_USERNAME:
    raise RuntimeError(
        "BOT_USERNAME não definido. Cria um ficheiro .env (ver .env.example) "
        "com a variável BOT_USERNAME=..."
    )

FORMS_LINK: Final = os.getenv("FORMS_LINK")
if not FORMS_LINK:
    raise RuntimeError(
        "FORMS_LINK não definido. Cria um ficheiro .env (ver .env.example) "
        "com a variável FORMS_LINK=..."
    )

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
