import os
import re
import html
import json
import uuid
import logging
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import requests
import yt_dlp

logger = logging.getLogger(__name__)

@dataclass
class MediaItem:
    file_path: Path
    media_type: str  # 'video' yoki 'photo'
    duration: Optional[int] = None

@dataclass
class DownloadResult:
    success: bool
    title: str = ""
    uploader: str = ""
    items: List[MediaItem] = None
    error_message: str = ""

    def __post_init__(self):
        if self.items is None:
            self.items = []

class InstagramDownloader:
    def __init__(self, download_dir: Path):
        self.download_dir = download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        })

    def extract_shortcode(self, url: str) -> Optional[str]:
        """Instagram URL dan post/reel ID (shortcode) sini ajratib olish"""
        patterns = [
            r"instagram\.com/(?:reel|reels|p|tv|share/reel)/([A-Za-z0-9_-]+)",
            r"instagram\.com/stories/[^/]+/([0-9]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _clean_json_string(self, raw: str) -> str:
        """JSON ichidagi unicode va escape belgilarni tozalash"""
        try:
            return json.loads(f'"{raw}"')
        except Exception:
            return raw.replace(r"\/", "/").replace(r"\u0026", "&")

    def _download_file(self, file_url: str, dest_path: Path, max_bytes: int = 50 * 1024 * 1024) -> bool:
        """URL dan faylni diskka oqim (stream) orqali yuklab olish"""
        try:
            with self.session.get(file_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                downloaded = 0
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if downloaded > max_bytes:
                                logger.warning(f"Fayl hajmi 50MB dan oshib ketdi: {dest_path}")
                                return False
            return dest_path.exists() and dest_path.stat().st_size > 0
        except Exception as e:
            logger.error(f"Faylni yuklab olishda xatolik: {e}")
            if dest_path.exists():
                dest_path.unlink()
            return False

    def _method_embed_scrape(self, shortcode: str, original_url: str) -> Optional[DownloadResult]:
        """
        1-USUL: Instagram rasmiy embed sahifasi orqali to'g'ridan-to'g'ri scraping.
        Hech qanday bot blokirovkasi yoki API kaliti talab qilmaydi!
        """
        embed_urls = [
            f"https://www.instagram.com/reel/{shortcode}/embed/captioned/",
            f"https://www.instagram.com/p/{shortcode}/embed/captioned/",
        ]

        for embed_url in embed_urls:
            try:
                resp = self.session.get(embed_url, timeout=12)
                if resp.status_code != 200 or len(resp.text) < 500:
                    continue

                page_text = resp.text

                # Video URL ni qidirish
                video_url = None
                v_match = re.search(r'"video_url"\s*:\s*"([^"]+)"', page_text)
                if v_match:
                    video_url = self._clean_json_string(v_match.group(1))
                else:
                    v_tag = re.search(r'<video[^>]+src="([^">]+)"', page_text)
                    if v_tag:
                        video_url = html.unescape(v_tag.group(1))

                # Muallif va tavsifni topish
                uploader = ""
                u_match = re.search(r'class="CaptionAuthor"[^>]*>([^<]+)</a>', page_text)
                if u_match:
                    uploader = u_match.group(1).strip()
                else:
                    u_json = re.search(r'"username"\s*:\s*"([^"]+)"', page_text)
                    if u_json:
                        uploader = self._clean_json_string(u_json.group(1))

                caption = ""
                c_match = re.search(r'<div class="Caption"[^>]*>(.*?)</div>', page_text, re.DOTALL)
                if c_match:
                    raw_caption = re.sub(r"<[^>]+>", " ", c_match.group(1))
                    caption = " ".join(raw_caption.split())
                    if len(caption) > 300:
                        caption = caption[:297] + "..."

                if video_url:
                    dest = self.download_dir / f"ig_{shortcode}_{uuid.uuid4().hex[:4]}.mp4"
                    if self._download_file(video_url, dest):
                        logger.info(f"Embed orqali video yuklandi: {dest}")
                        return DownloadResult(
                            success=True,
                            title=caption,
                            uploader=uploader,
                            items=[MediaItem(file_path=dest, media_type="video")]
                        )

                # Agar video bo'lmasa, rasm bo'lishi mumkin
                img_match = re.search(r'"display_url"\s*:\s*"([^"]+)"', page_text)
                if img_match:
                    photo_url = self._clean_json_string(img_match.group(1))
                    dest = self.download_dir / f"ig_{shortcode}_{uuid.uuid4().hex[:4]}.jpg"
                    if self._download_file(photo_url, dest):
                        logger.info(f"Embed orqali rasm yuklandi: {dest}")
                        return DownloadResult(
                            success=True,
                            title=caption,
                            uploader=uploader,
                            items=[MediaItem(file_path=dest, media_type="photo")]
                        )

            except Exception as e:
                logger.warning(f"Embed usulida xatolik: {e}")

        return None

    def _method_ytdlp(self, url: str) -> Optional[DownloadResult]:
        """
        2-USUL: yt-dlp dvigateli orqali yuklash.
        """
        job_id = uuid.uuid4().hex[:8]
        ydl_opts = {
            "outtmpl": f"{self.download_dir}/{job_id}_%(autonumber)s.%(ext)s",
            "format": "best[filesize<50M]/bestvideo[filesize<45M]+bestaudio/best",
            "merge_output_format": "mp4",
            "writethumbnail": False,
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "max_filesize": 50 * 1024 * 1024,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 324.0.0.18.109"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    return None

                title = info.get("title") or info.get("description") or ""
                if len(title) > 300:
                    title = title[:297] + "..."

                uploader = info.get("uploader") or info.get("channel") or ""

                matching_files = sorted(list(self.download_dir.glob(f"{job_id}_*")))
                if not matching_files and "id" in info:
                    matching_files = sorted(list(self.download_dir.glob(f"*{info['id']}*")))

                media_items: List[MediaItem] = []
                for file_path in matching_files:
                    ext = file_path.suffix.lower()
                    if ext in [".mp4", ".mov", ".m4v", ".webm", ".mkv"]:
                        m_type = "video"
                    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
                        m_type = "photo"
                    else:
                        continue

                    if file_path.stat().st_size > 50 * 1024 * 1024:
                        continue

                    media_items.append(
                        MediaItem(
                            file_path=file_path,
                            media_type=m_type,
                            duration=info.get("duration")
                        )
                    )

                if media_items:
                    return DownloadResult(
                        success=True,
                        title=title,
                        uploader=uploader,
                        items=media_items
                    )
        except Exception as e:
            logger.warning(f"yt-dlp xatoligi: {e}")

        return None

    def _method_cobalt_api(self, url: str) -> Optional[DownloadResult]:
        """
        3-USUL: Cobalt ommaviy bepul API orqali yuklash zaxirasi.
        """
        cobalt_endpoints = [
            "https://api.cobalt.tools",
            "https://cobalt-api.kwiatekm.tokyo",
        ]

        for endpoint in cobalt_endpoints:
            try:
                resp = requests.post(
                    endpoint,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    json={"url": url},
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status")
                    
                    # Bitta video/audio URL
                    if status in ["stream", "redirect", "tunnel"]:
                        media_url = data.get("url")
                        if media_url:
                            dest = self.download_dir / f"ig_cobalt_{uuid.uuid4().hex[:6]}.mp4"
                            if self._download_file(media_url, dest):
                                return DownloadResult(
                                    success=True,
                                    title="",
                                    uploader="",
                                    items=[MediaItem(file_path=dest, media_type="video")]
                                )
                    # Karusel yoki bir nechta fayl
                    elif status == "picker":
                        picker = data.get("picker", [])
                        items = []
                        for p in picker[:10]:
                            p_url = p.get("url")
                            p_type = p.get("type", "video")
                            ext = ".mp4" if p_type == "video" else ".jpg"
                            dest = self.download_dir / f"ig_cobalt_{uuid.uuid4().hex[:6]}{ext}"
                            if self._download_file(p_url, dest):
                                items.append(MediaItem(file_path=dest, media_type=p_type))
                        if items:
                            return DownloadResult(
                                success=True,
                                items=items
                            )
            except Exception as e:
                logger.warning(f"Cobalt API {endpoint} xatoligi: {e}")

        return None

    def _sync_download(self, url: str) -> DownloadResult:
        """3 xil usul bo'yicha ketma-ket yuklab olishni sinab ko'radi"""
        shortcode = self.extract_shortcode(url)

        # 1-usul: Rasmiy Embed sahifasi (juda tez va login talab qilmaydi)
        if shortcode:
            logger.info(f"1-usul (Embed Scrape) sinab ko'rilmoqda: {shortcode}")
            result = self._method_embed_scrape(shortcode, url)
            if result and result.success:
                return result

        # 2-usul: yt-dlp
        logger.info(f"2-usul (yt-dlp) sinab ko'rilmoqda: {url}")
        result = self._method_ytdlp(url)
        if result and result.success:
            return result

        # 3-usul: Cobalt bepul API zaxirasi
        logger.info(f"3-usul (Cobalt API) sinab ko'rilmoqda: {url}")
        result = self._method_cobalt_api(url)
        if result and result.success:
            return result

        # Agar hech qaysi usul ishlamasa
        return DownloadResult(
            success=False,
            error_message=(
                "Ushbu postni yuklab bo'lmadi.\n"
                "Mumkin bo'lgan sabablar:\n"
                "1. Profil yoki post yopiq (private).\n"
                "2. Havola noto'g'ri yoki post o'chirilgan.\n"
                "3. Fayl hajmi 50 MB dan katta."
            )
        )

    async def download(self, url: str) -> DownloadResult:
        """Asinxron chaqiruvchi"""
        return await asyncio.to_thread(self._sync_download, url)

    def cleanup(self, items: List[MediaItem]):
        """Yuborib bo'lingan fayllarni diskdan tozalash"""
        for item in items:
            try:
                if item.file_path.exists():
                    item.file_path.unlink()
            except Exception as e:
                logger.error(f"Faylni o'chirishda xatolik {item.file_path}: {e}")
