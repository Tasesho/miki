from __future__ import annotations

from io import BytesIO
from textwrap import wrap

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps

from dashboard.welcome_cards import WelcomeCardSettings


class WelcomeCardRenderer:
    width = 1024
    height = 500
    max_background_bytes = 15 * 1024 * 1024

    def __init__(self):
        self._background_cache: dict[str, Image.Image] = {}

    async def render(
        self,
        settings: WelcomeCardSettings,
        member_name: str,
        member_count: int,
        avatar_url: str | None,
    ) -> BytesIO:
        image = await self._background(settings)
        draw = ImageDraw.Draw(image)
        text_color = settings.text_color
        accent_color = settings.accent_color
        text_x = 132 if settings.show_avatar else 34
        content_height = 116 if settings.show_member_count else 88
        content_y = (self.height - content_height) // 2
        if settings.show_avatar:
            avatar = await self._avatar(avatar_url, member_name, accent_color)
            image.paste(avatar, (34, (self.height - 76) // 2), avatar)

        title = settings.title.replace("{user}", member_name).replace("{server}", "this server")
        message = settings.message.replace("{user}", member_name).replace("{server}", "this server")
        title_font = ImageFont.load_default(size=32)
        body_font = ImageFont.load_default(size=16)
        small_font = ImageFont.load_default(size=13)
        draw.text((text_x, content_y), title, fill=text_color, font=title_font)
        y_position = content_y + 48
        for line in wrap(message, width=65 if settings.show_avatar else 90):
            draw.text((text_x, y_position), line, fill=text_color, font=body_font)
            y_position += 23
        if settings.show_member_count:
            draw.text(
                (text_x, content_y + 91),
                f"You are member #{member_count:,}",
                fill=text_color,
                font=small_font,
            )

        output = BytesIO()
        image.convert("RGB").save(output, format="PNG", optimize=True)
        output.seek(0)
        return output

    async def _background(self, settings: WelcomeCardSettings) -> Image.Image:
        if settings.background_url in self._background_cache:
            image = ImageOps.fit(
                self._background_cache[settings.background_url].convert("RGB"),
                (self.width, self.height),
            )
            return Image.blend(image, Image.new("RGB", image.size, "black"), 0.35)
        downloaded = (
            await self._download_image(settings.background_url) if settings.background_url else None
        )
        if downloaded is not None:
            if settings.background_url:
                self._background_cache[settings.background_url] = downloaded.copy()
            image = ImageOps.fit(downloaded.convert("RGB"), (self.width, self.height))
            return Image.blend(image, Image.new("RGB", image.size, "black"), 0.35)

        start = Image.new("RGB", (self.width, self.height), settings.accent_color)
        end = Image.new("RGB", (self.width, self.height), "#252B55")
        gradient = Image.new("RGB", start.size)
        start_pixels = start.load()
        end_pixels = end.load()
        gradient_pixels = gradient.load()
        for x in range(self.width):
            for y in range(self.height):
                factor = (x / self.width + y / self.height) / 2
                gradient_pixels[x, y] = tuple(
                    round(
                        start_pixels[x, y][index] * (1 - factor) + end_pixels[x, y][index] * factor
                    )
                    for index in range(3)
                )
        return Image.blend(gradient, Image.new("RGB", gradient.size, "black"), 0.18)

    async def _avatar(self, url: str | None, name: str, color: str) -> Image.Image:
        avatar = await self._download_image(url) if url else None
        if avatar is None:
            avatar = Image.new("RGB", (68, 68), color)
            ImageDraw.Draw(avatar).text(
                (24, 20), name[:1].upper(), fill="white", font=ImageFont.load_default(size=28)
            )
        avatar = avatar.convert("RGB").resize((68, 68))
        mask = Image.new("L", (76, 76), 0)
        ImageDraw.Draw(mask).ellipse((4, 4, 71, 71), fill=255)
        result = Image.new("RGBA", (76, 76), "white")
        result.paste(avatar, (4, 4), mask.crop((4, 4, 72, 72)))
        return result

    async def _download_image(self, url: str) -> Image.Image | None:
        if not url.startswith("https://"):
            return None
        timeout = aiohttp.ClientTimeout(total=5)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status != 200 or response.url.scheme != "https":
                        return None
                    payload = bytearray()
                    async for chunk in response.content.iter_chunked(64 * 1024):
                        payload.extend(chunk)
                        if len(payload) > self.max_background_bytes:
                            return None
            image = Image.open(BytesIO(payload))
            image.load()
            return image
        except (aiohttp.ClientError, OSError, ValueError):
            return None
