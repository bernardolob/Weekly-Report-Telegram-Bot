from datetime import time as dtime
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Final
from sheetsReader import refresh_cache, getTWILList, getWeeklyReportMessage, getTWILResponsible
import sys
import logging

logging.basicConfig(
    filename="logs/telegrambot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


FIRST_WARNING_MESSAGE: str = """
📣 #WeeklyReport time!
🕙 Deadline: 23:59 WEST
💡 TWIL Reminder: {twil_responsible}
🔗 Link: https://forms.gle/XkYLXHCKF9HEur6s9
"""


# WHITELIST: list[int] = [-1001279975882, -5068062676]
WHITELIST: list[int] = [-5068062676]


TOKEN: Final = '8084223298:AAF0bnTCct6D99FPHul1ezTse5cS7jLQFsM'
BOT_USERNAME: Final = '@saobernardo_bot'

### FUNCTIONS

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info(f'Update {update} caused error {context.error}')


async def sendWarning1(context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Second warning message request.")
    await refresh_cache()
    chat_id = context.job.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text=FIRST_WARNING_MESSAGE.format(twil_responsible=await getTWILResponsible()),
        disable_web_page_preview=True
    )


################################ MAIN ################################



def main():
    try:
        logging.info("Starting bot...")
        app = Application.builder().token(TOKEN).build()

        # Errors
        app.add_error_handler(error)

        # Auto start weekly messages
        for chat_id in WHITELIST:
            sendWarning1(app.job_queue, chat_id)

    except SystemExit:
        logging.info("SystemExit called. Bot stopped.")
    finally:
        logging.info("Bot shutdown complete.")
        sys.exit(0)




if __name__ == '__main__':
    main()
