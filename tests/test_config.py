from config import Settings


def test_settings_supports_environment_overrides(monkeypatch, tmp_path):
    db_path = tmp_path / "miki.db"
    monkeypatch.setenv("MIKI_ENV", "staging")
    monkeypatch.setenv("DISCORD_TOKEN", "token")
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("COMMAND_PREFIX", "?")

    settings = Settings.from_env(require_token=True)

    assert settings.environment == "staging"
    assert settings.discord_token == "token"
    assert settings.database_path == str(db_path)
    assert settings.command_prefix == "?"


def test_settings_import_safe_without_token(monkeypatch, tmp_path):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("TOKEN", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "miki.db"))

    settings = Settings.from_env()

    assert settings.discord_token == ""
