import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Carrega variáveis do ficheiro .env para o ambiente
load_dotenv()

cached_WR_message = None
cached_TWIL_responsible = None
cached_TWIL_list = None

# Caminho para o JSON da service account, vindo do .env
CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not CREDS_PATH:
    raise RuntimeError(
        "GOOGLE_APPLICATION_CREDENTIALS não definido. Cria um ficheiro .env "
        "(ver .env.example) com o caminho para o JSON da service account."
    )

creds = Credentials.from_service_account_file(
    CREDS_PATH,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(creds)

WRFinalModelPage = client.open("Reporte Semanal | Lobões").sheet1
TWILPage = client.open("Reporte Semanal | Lobões").worksheet("TWIL")
TWILOrderPage = client.open("Reporte Semanal | Lobões").worksheet("TWIL Ordem")


async def refresh_cache():
    global cached_WR_message, cached_TWIL_responsible, cached_TWIL_list
    try:
        cached_WR_message = WRFinalModelPage.acell("F4").value or "⚠️ Weekly Report (cell F4) is empty!"
        cached_TWIL_responsible = TWILPage.acell("F13").value or "Unknown"
        cached_TWIL_list = TWILOrderPage.col_values(4)[2:] or ["No data"]
        print("Cache refreshed.")
    except Exception as e:
        print("Cache refresh error:", e)


async def getWeeklyReportMessage():
    return cached_WR_message

async def getTWILResponsible():
    return cached_TWIL_responsible

async def getTWILList():
    return cached_TWIL_list