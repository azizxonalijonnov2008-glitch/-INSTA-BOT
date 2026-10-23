import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Asosiy konfiguratsiya
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID lari (vergul bilan ajratilgan holda ko'rsatilishi mumkin: 12345,67890)
ADMIN_IDS = [
    int(x.strip()) 
    for x in os.getenv("ADMIN_IDS", "").split(",") 
    if x.strip().isdigit()
]

# Yuklab olingan vaqtinchalik fayllar saqlanadigan papka
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Telegram botlari orqali yuborish mumkin bo'lgan maksimal hajm (50 MB)
MAX_FILE_SIZE_MB = 50
