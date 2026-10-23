from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router(name="start_router")

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Qanday ishlatiladi?", callback_data="help_info")
    builder.button(text="ℹ️ Bot haqida", callback_data="about_info")
    builder.adjust(2)
    return builder.as_markup()

@router.message(CommandStart())
async def handle_start(message: types.Message):
    user_name = message.from_user.first_name or "Foydalanuvchi"
    text = (
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        "📥 <b>Instagram Video & Rasm Yuklovchi Botga xush kelibsiz!</b>\n\n"
        "Menga Instagram’dan istalgan <b>Reels</b>, <b>Post</b> yoki <b>Video</b> havolasini yuboring, "
        "men uni bir necha soniyada yuklab beraman.\n\n"
        "<i>Sinab ko'rish uchun Instagram havolasini yuboring! 🚀</i>"
    )
    await message.answer(text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def handle_help(message: types.Message):
    help_text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "1. Instagram ilovasiga kiring.\n"
        "2. O'zingizga yoqqan Reel yoki Postdagi <b>Ulashish (Share)</b> tugmasini bosing.\n"
        "3. <b>Havolani nusxalash (Copy link)</b> ni tanlang.\n"
        "4. Nusxalangan havolani ushbu botga xabar sifatida yuboring.\n\n"
        "⚠️ <i>Eslatma:</i>\n"
        "• Faqat <b>ochiq (public)</b> profillardagi post va reelslar yuklanadi.\n"
        "• Yopiq (private) profillardan yuklab bo'lmaydi.\n"
        "• Telegram cheklovi tufayli 50 MB dan katta videolar yuklanmasligi mumkin."
    )
    await message.answer(help_text)

@router.callback_query(F.data == "help_info")
async def callback_help(callback: types.CallbackQuery):
    help_text = (
        "📖 <b>Qanday ishlatiladi?</b>\n\n"
        "1. Instagram'dan havolani nusxalang.\n"
        "2. Botga yuboring.\n"
        "3. Bot bir necha soniyada faylni yuklab jo'natadi! ✅\n\n"
        "<i>Faqat ochiq (public) akkaunt havolalari qo'llab-quvvatlanadi.</i>"
    )
    await callback.message.answer(help_text)
    await callback.answer()

@router.callback_query(F.data == "about_info")
async def callback_about(callback: types.CallbackQuery):
    about_text = (
        "ℹ️ <b>Bot haqida ma'lumot:</b>\n\n"
        "• Dasturlash tili: <b>Python 3</b>\n"
        "• Asosiy kutubxona: <b>aiogram 3.x</b>\n"
        "• Yuklash mexanizmi: <b>yt-dlp</b>\n"
        "• Tezkor, xavfsiz va qulay.\n\n"
        "Savol yoki takliflar bo'lsa bemalol murojaat qilishingiz mumkin."
    )
    await callback.message.answer(about_text)
    await callback.answer()
