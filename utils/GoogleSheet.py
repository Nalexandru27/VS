import gspread
from google.oauth2.service_account import Credentials

# 🔹 1. Configurare Service Account
SERVICE_ACCOUNT_FILE = "path_to_your_service_account.json"  # Înlocuiește cu calea fișierului JSON
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# 🔹 2. Accesează Google Sheets
SHEET_NAME = "Numele_Foii_de_Calcul"  # Asigură-te că ai acest document în Google Drive
sheet = client.open(SHEET_NAME).sheet1  # Deschide primul sheet

# 🔹 3. Scrie date în Google Sheets
data = [
    ["Date", "AAPL", "MSFT"],
    ["2024-02-23", 187.23, 410.54],
    ["2024-02-22", 185.76, 408.12]
]

sheet.clear()  # Șterge datele existente
sheet.update(data)  # Scrie datele noi

print("✅ Google Sheet actualizat cu succes!")
