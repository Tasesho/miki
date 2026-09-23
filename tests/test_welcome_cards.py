import pytest

from dashboard.welcome_cards import WelcomeCardSettings, WelcomeCardValidationError
from services.welcome_card_service import WelcomeCardService


def test_welcome_card_settings_accept_valid_dashboard_payload():
    settings = WelcomeCardSettings.from_payload(
        {"enabled": True, "channel_id": 987, "title": "Hello {user}", "accent_color": "#0EA5E9"}
    )

    assert settings.enabled is True
    assert settings.channel_id == 987
    assert settings.title == "Hello {user}"
    assert settings.accent_color == "#0EA5E9"
    assert settings.show_avatar is True
    assert settings.to_dict()["channel_id"] == "987"


def test_welcome_card_settings_preserves_discord_snowflakes():
    settings = WelcomeCardSettings.from_payload({"channel_id": "1552382029264322591"})

    assert settings.channel_id == 1552382029264322591
    assert settings.to_dict()["channel_id"] == "1552382029264322591"


def test_welcome_message_template_mentions_user():
    guild = type("Guild", (), {"name": "Miki", "text_channels": [], "roles": []})()
    channel = type("Channel", (), {"mention": "<#456>", "name": "welcome"})()
    member = type("Member", (), {"mention": "<@123>", "display_name": "Tase"})()

    content = WelcomeCardService._message_content(
        "Bienvenido a {server.name}, {user}! Ve a {channel}.", member, guild, channel
    )

    assert content == "Bienvenido a Miki, <@123>! Ve a <#456>."


@pytest.mark.parametrize(
    "payload", [{"accent_color": "blue"}, {"channel_id": -1}, {"unknown": True}]
)
def test_welcome_card_settings_reject_invalid_payload(payload):
    with pytest.raises(WelcomeCardValidationError):
        WelcomeCardSettings.from_payload(payload)
