import re
import logging
from pathlib import Path
from typing import List

from aiogram import Router, types, F, Bot
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import DOWNLOADS_DIR
from services.downloader import InstagramDownloader, DownloadResult

logger = logging.getLogger(__name__)

router = Router(name="instagram_router")
downloader = InstagramDownloader(DOWNLOADS_DIR)

# Instagram havolalarini aniqlash uchun regex
INSTAGRAM_URL_REGEX = re.compile(
    r"(https?://(?:www\.)?instagram\.com/(?:[a-zA-Z0-9_\.]+/)?(?:p|reel|reels|tv|stories|share/reel)/[a-zA-Z0-9_\-]+[^\s]*)"
)

def create_media_keyboard(url: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Instagramda ochish", url=url)
    return builder.as_markup()

@router.message(F.text.regexp(INSTAGRAM_URL_REGEX))
async def handle_instagram_link(message: types.Message, bot: Bot):
    # Xabardagi barcha instagram havolalarini topamiz
    matches = INSTAGRAM_URL_REGEX.findall(message.text)
    if not matches:
        return

    url = matches[0]
    loading_msg = await message.reply("⏳ <b>Instagram'dan yuklanmoqda...</b>\n<i>Iltimos, ozgina kuting.</i>")

    download_result: DownloadResult = None
    try:
        # Chatda foydalanuvchiga harakatni ko'rsatish
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

        # Videoni/rasmni yuklab olish (alohida thread orqali asinxron)
        download_result = await downloader.download(url)

        if not download_result.success or not download_result.items:
            error_text = (
                f"❌ <b>Yuklab bo'lmadi!</b>\n\n"
                f"{download_result.error_message or 'Noma\'lum xatolik yuz berdi.'}\n\n"
                f"💡 <i>Tekshiring:</i>\n"
                f"1. Profil ochiq (public) ekanligiga ishonch hosil qiling.\n"
                f"2. Havola to'g'ri nusxalanganligini tekshiring."
            )
            await loading_msg.edit_text(error_text)
            return

        # Sarlavha tayyorlash
        caption = ""
        if download_result.uploader:
            caption += f"👤 <b>Muallif:</b> @{download_result.uploader}\n"
        if download_result.title:
            caption += f"📝 {download_result.title}\n\n"
        caption += "🤖 @InstaDownloaderBot orqali yuklandi"

        reply_markup = create_media_keyboard(url)

        # Agar bitta fayl bo'lsa
        if len(download_result.items) == 1:
            item = download_result.items[0]
            media_file = FSInputFile(str(item.file_path))

            if item.media_type == "video":
                await message.reply_video(
                    video=media_file,
                    caption=caption,
                    duration=item.duration or 0,
                    reply_markup=reply_markup
                )
            else:
                await message.reply_photo(
                    photo=media_file,
                    caption=caption,
                    reply_markup=reply_markup
                )

        # Agar bir nechta fayl (karusel) bo'lsa
        else:
            # Telegram media guruhi maksimum 10 ta element qabul qiladi
            chunk_size = 10
            items = download_result.items[:10]  # dastlabki 10 tasini olamiz
            
            media_group = []
            for i, item in enumerate(items):
                file_obj = FSInputFile(str(item.file_path))
                item_caption = caption if i == 0 else ""
                
                if item.media_type == "video":
                    media_group.append(InputMediaVideo(media=file_obj, caption=item_caption))
                else:
                    media_group.append(InputMediaPhoto(media=file_obj, caption=item_caption))

            await message.reply_media_group(media=media_group)
            await message.answer("🔗 Original post:", reply_markup=reply_markup)

        # Yuklanmoqda xabarini o'chirish
        await loading_msg.delete()

    except Exception as e:
        logger.exception("Faylni yuborishda xatolik:")
        await loading_msg.edit_text(
            f"❌ <b>Xatolik yuz berdi:</b>\n<code>{str(e)[:150]}</code>"
        )
    finally:
        # Fayllarni diskdan o'chirib tozalash
        if download_result and download_result.items:
            downloader.cleanup(download_result.items)
