from PIL import Image

from dashboard.welcome_cards import WelcomeCardSettings
from services.welcome_card_renderer import WelcomeCardRenderer


async def test_renderer_creates_png_without_remote_images():
    image = await WelcomeCardRenderer().render(
        WelcomeCardSettings(enabled=True, title="Welcome, {user}!", message="Hello there."),
        "Miki fan",
        42,
        None,
    )

    rendered = Image.open(image)

    assert rendered.format == "PNG"
    assert rendered.size == (1024, 500)


async def test_renderer_uses_background_image(monkeypatch):
    async def fake_download(_url):
        return Image.new("RGB", (20, 20), "#FF0000")

    renderer = WelcomeCardRenderer()
    monkeypatch.setattr(renderer, "_download_image", fake_download)
    output = await renderer.render(
        WelcomeCardSettings(background_url="https://example.com/background.png"),
        "Miki fan",
        42,
        None,
    )

    rendered = Image.open(output).convert("RGB")

    assert rendered.getpixel((512, 20))[0] > rendered.getpixel((512, 20))[2]
