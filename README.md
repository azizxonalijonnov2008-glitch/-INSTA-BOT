# 📥 Instagram Downloader Telegram Bot (Python)

Ushbu Telegram bot Instagram'dagi **Reels**, **Postlar**, **Videolar** va **Rasmlar**ni yuklab olib, to'g'ridan-to'g'ri Telegram foydalanuvchisiga yuborib berish uchun yaratilgan.

---

## 🌟 Asosiy imkoniyatlari
- ⚡ **Tezkor yuklash**: Zamonaviy `yt-dlp` dvigateli asosida ishlaydi.
- 📱 **Har xil formatlarni qo'llab-quvvatlash**:
  - Instagram Reels
  - Instagram Videolari (Postlar)
  - Instagram Rasmlari (bittalik va karusel - bir nechta rasm/video)
- 🤖 **Zamonaviy arxitektura**: Python 3 va `aiogram 3.x` (asinxron, tezkor va xavfsiz).
- 🧹 **Avtomatik tozalash**: Yuborilgan fayllar server/kompyuter diskida joy egallamasligi uchun avtomatik o'chirib tashlanadi.
- 🏷 **Post ma'lumotlari**: Muallif nomi, post sarlavhasi va original postga havola biriktiriladi.

---

## 📁 Loyiha tuzilishi

```
instagram_downloader_bot/
│
├── config.py                 # Bot konfiguratsiyasi va sozlamalar
├── main.py                   # Botni ishga tushiruvchi asosiy fayl
├── requirements.txt          # Kerakli Python kutubxonalari
├── .env                      # Bot tokeni saqlanadigan fayl
├── .env.example              # Namuna .env fayli
├── install_requirements.bat  # Kutubxonalarni 1 marta bosish bilan o'rnatish
├── run.bat                   # Botni 1 marta bosish bilan ishga tushirish
│
├── handlers/                 # Telegram xabar ishlovchilari
│   ├── __init__.py
│   ├── start.py              # /start, /help va inline tugmalar
│   └── instagram.py          # Instagram havolalarini tutib yuklash
│
├── services/                 # Xizmatlar
│   ├── __init__.py
│   └── downloader.py         # yt-dlp asosidagi asinxron yuklagich
│
└── downloads/                # Vaqtinchalik fayllar papkasi
```

---

## 🚀 O'rnatish va Ishga tushirish (Qadamma-qadam)

### 1-qadam: Bot Tokenini olish
1. Telegram'da [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botga nom va `@username` (masalan, `MyInstaDownloader_bot`) bering.
4. `@BotFather` sizga **API Token** beradi (masalan: `123456789:ABCdefGHIjklMNOpqrs`).

### 2-qadam: Tokenni sozlash
Loyihadagi `.env` faylini oching va tokenni yozing:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrs
```

### 3-qadam: Kutubxonalarni o'rnatish
Windows'da:
- Shunchaki **`install_requirements.bat`** faylini ikki marta bosing.
- Yoki terminal / buyruqlar satrida quyidagini bajaring:
  ```bash
  pip install -r requirements.txt
  ```

### 4-qadam: Botni ishga tushirish
- Windows'da shunchaki **`run.bat`** faylini ikki marta bosing!
- Yoki terminalda:
  ```bash
  python main.py
  ```

Bot ishga tushgach, konsolda:
```
🚀 Bot faol: https://t.me/SizningBotUsername
```
yozuvi chiqadi.

---

## 💡 Botdan qanday foydalaniladi?
1. Botga o'ting va `/start` tugmasini bosing.
2. Instagram ilovasida istalgan video yoki reel postining **"Ulashish (Share) -> Havolani nusxalash (Copy link)"** tugmasini bosing.
3. Havolani botga yuboring.
4. Bot bir necha soniyada videoni yuklab jo'natadi! 📥

---

## ⚠️ Muhim eslatmalar:
1. **Yopiq (Private) profillar**: Instagram xavfsizlik qoidalariga ko'ra, yopiq profillardagi postlarni yuklab bo'lmaydi. Faqat ochiq (public) postlar yuklanadi.
2. **50 MB cheklovi**: Telegram oddiy botlar uchun bitta faylni yuborishda maksimal 50 MB hajm belgilagan. 50 MB dan katta videolar yuklanmasligi mumkin.
