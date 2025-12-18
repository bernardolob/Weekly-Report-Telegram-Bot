from datetime import time as dtime
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Final
from timeStructure import TimeStructure
from sheetsReader import refresh_cache, getTWILList, getWeeklyReportMessage, getTWILResponsible
import sys
import signal
import logging

logging.basicConfig(
    filename="logs/telegrambot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)




################################ CONSTANTS ################################


WHITELIST: list[int] = [-1001279975882, -5068062676]
# WHITELIST: list[int] = [-5068062676]


# DAYS:    0 - Sunday, 1 - Monday, ...  6 - Saturday
firstWarningTime  = TimeStructure(12, 00, (0,))
secondWarningTime = TimeStructure(21, 00, (0,))
WeeklyReportTime  = TimeStructure( 8, 00, (1,))

TOKEN: Final = '8084223298:AAF0bnTCct6D99FPHul1ezTse5cS7jLQFsM'
BOT_USERNAME: Final = '@saobernardo_bot'

START_WR_MESSAGE: str = f"""
<b>✅ As mensagens semanais estão ligadas.
Serão mandadas as seguintes mensagens:</b>
📣 Primeiro aviso para preencher o forms no Domingo às {firstWarningTime.__str__()}.
🚨 Segundo avido para preencher o forms no Domingo às {secondWarningTime.__str__()}.
📰 Reporte Semanal de São Bernardo na Segunda-feira às {WeeklyReportTime.__str__()}.
"""

FIRST_WARNING_MESSAGE: str = """
📣 #WeeklyReport time!
🕙 Deadline: 23:59 WEST
💡 TWIL Reminder: {twil_responsible}
🔗 Link: https://forms.gle/XkYLXHCKF9HEur6s9
"""

SECOND_WARNING_MESSAGE: str = """
🚨 #WeeklyReport last call!
⏳ Few hours left!
💡 TWIL Reminder: {twil_responsible}
🔗 Link: https://forms.gle/XkYLXHCKF9HEur6s9
"""

TWIL_RESPONSIBLE_MESSAGE: str = """
This week {twil_responsible} is responsible for the TWIL segment.
"""

HELP_MESSAGE: str = """
/startwr - Starts sending WR messages weekly automatically.
/stopwr - Stops sending weekly messages.
/help - Lists possible commands.
/sendnow - Sends the Weekly Report instantly.
/twilresponsible - Shows who is responsible for the TWIL this week.
/listtwil - Lists the upcomming TWIL responsibles.
"""

STOP_MESSAGE: str = """
❌ Stopped sending weekly messages!
"""

############################## AUX METHODS ##############################

def shutdown_handler(signum, frame):
    logging.info("Shutdown signal received. Exiting cleanly.")
    sys.exit(0)

def is_allowed_chat(update: Update) -> bool:
    return update.effective_chat.id in WHITELIST


def schedule_wr_jobs(job_queue, chat_id):
    # Remove old jobs
    current_jobs = job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    job_queue.run_daily(
        firstWarning_message,
        time=dtime(hour=firstWarningTime.hours, minute=firstWarningTime.minutes),
        days=firstWarningTime.days,
        chat_id=chat_id,
        name=str(chat_id)
    )

    job_queue.run_daily(
        secondWarning_message,
        time=dtime(hour=secondWarningTime.hours, minute=secondWarningTime.minutes),
        days=secondWarningTime.days,
        chat_id=chat_id,
        name=str(chat_id)
    )

    job_queue.run_daily(
        WR_message,
        time=dtime(hour=WeeklyReportTime.hours, minute=WeeklyReportTime.minutes),
        days=WeeklyReportTime.days,
        chat_id=chat_id,
        name=str(chat_id)
    )


################################ COMMANDS ################################



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Help request.")
    if (not is_allowed_chat(update)):
        logging.warning(f"UNALLOWED CHAT: {update.effective_chat.id}")
        return
    await update.message.reply_text(HELP_MESSAGE)
    logging.info(f'HELP : Id ({update.message.chat.id}) in {update.message.chat.type}')



async def firstWarning_message(context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("First warning message request.")
    await refresh_cache()
    chat_id = context.job.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text=FIRST_WARNING_MESSAGE.format(twil_responsible=await getTWILResponsible()),
        disable_web_page_preview=True
    )



async def secondWarning_message(context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Second warning message request.")
    await refresh_cache()
    chat_id = context.job.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text=SECOND_WARNING_MESSAGE.format(twil_responsible=await getTWILResponsible()),
        disable_web_page_preview=True
    )



async def WR_message(context: ContextTypes.DEFAULT_TYPE, manual_chat_id=None):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Weekly Report message request.")
    await refresh_cache()

    chat_id = manual_chat_id or context.job.chat_id

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=await getWeeklyReportMessage(),
        disable_web_page_preview=True,
        parse_mode="HTML"
    )
    await msg.pin()



async def stopWR(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Stop WR request.")
    if (not is_allowed_chat(update)):
        logging.warning(f"UNALLOWED CHAT: {update.effective_chat.id}")
        return
    chat_id = update.message.chat_id

    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    await update.message.reply_text(STOP_MESSAGE)
    logging.info(f'STOPWR : User ({update.message.chat.id}) in {update.message.chat.type}')



async def startWR(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Start WR request.")
    if (not is_allowed_chat(update)):
        logging.warning(f"UNALLOWED CHAT: {update.effective_chat.id}")
        return
    chat_id = update.message.chat_id

    schedule_wr_jobs(context.job_queue, chat_id)

    await update.message.reply_text(START_WR_MESSAGE, parse_mode="HTML")
    logging.info(f'STARTWR : User ({update.message.chat.id}) in {update.message.chat.type}')



async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info(f'Update {update} caused error {context.error}')



async def sendNow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Send now request.")
    if (not is_allowed_chat(update)):
        logging.warning(f"UNALLOWED CHAT: {update.effective_chat.id}")
        return
    chat_id = update.message.chat_id
    await WR_message(context, manual_chat_id=chat_id)
    logging.info(f'SENDNOW : User ({update.message.chat.id}) in {update.message.chat.type}')



async def showTWILresponsible(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Twil responsible request.")
    if (not is_allowed_chat(update)):
        logging.warning(f"UNALLOWED CHAT: {update.effective_chat.id}")
        return
    await refresh_cache()
    await update.message.reply_text(TWIL_RESPONSIBLE_MESSAGE.format(twil_responsible=await getTWILResponsible()))
    logging.info(f'TWILRESPONSIBLE : User ({update.message.chat.id}) in {update.message.chat.type}')



async def showTWILList(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("-----------")
    logging.info(datetime.now())
    logging.info("Twil list request.")
    if (not is_allowed_chat(update)):
        logging.warning(f"UNALLOWED CHAT: {update.effective_chat.id}")
        return
    await refresh_cache()
    twil_list = await getTWILList()  # call the function
    msg = "List of the upcoming TWIL responsibilities:\n"

    for m in twil_list:
        msg += f"- {m}\n"  # append each member

    await update.message.reply_text(msg)
    logging.info(f'LISTTWIL : User ({update.message.chat.id}) in {update.message.chat.type}')



################################ MAIN ################################



def main():
    logging.info("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("startwr", startWR))
    app.add_handler(CommandHandler("stopwr", stopWR))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler("sendnow", sendNow))
    app.add_handler(CommandHandler("twilresponsible", showTWILresponsible))
    app.add_handler(CommandHandler("listtwil", showTWILList))

    # Messages
    # app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Auto start weekly messages
    for chat_id in WHITELIST:
        schedule_wr_jobs(app.job_queue, chat_id)


    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    try:
        logging.info("Polling...")
        app.run_polling(poll_interval=3)
    except SystemExit:
        logging.info("SystemExit called. Bot stopped.")
    finally:
        logging.info("Bot shutdown complete.")



if __name__ == '__main__':
    main()








# Responses
# def handle_response(text: str) -> str:
#     if 'olá' in text.lower() or 'ola' in text.lower():
#         return 'Olá, estudo bem?'
#     else :
#         return 'Não percebi o que disse... mas sabia que São Bernardo era de Claraval? :)'



# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     messageType: str = update.message.chat.type
#     text: str = update.message.text
#     logging.info(f'User ({update.message.chat.id}) in {messageType}')

#     if messageType == 'group':
#         if BOT_USERNAME in update.message.text:
#             newText: str = text.replace(BOT_USERNAME, '').strip()
#             response: str = handle_response(newText)
#             await update.message.reply_text(response)
#         else:
#             return
#     else:
#         response: str = handle_response(text)
#         await update.message.reply_text(response)
#     logging.info('bot: ', response)

