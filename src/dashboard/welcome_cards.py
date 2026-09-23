from __future__ import annotations

from dataclasses import asdict, dataclass


class WelcomeCardValidationError(ValueError):
    """Raised when dashboard input is not safe to persist."""


@dataclass(frozen=True)
class WelcomeCardSettings:
    enabled: bool = False
    channel_id: int | None = None
    title: str = "Welcome, {user}!"
    message: str = "We are happy to have you here."
    extra_message: str = ""
    background_url: str | None = None
    accent_color: str = "#8B5CF6"
    text_color: str = "#FFFFFF"
    show_avatar: bool = True
    show_member_count: bool = True

    @classmethod
    def from_payload(cls, payload: dict) -> WelcomeCardSettings:
        if not isinstance(payload, dict):
            raise WelcomeCardValidationError("A JSON object is required.")
        allowed = set(cls.__dataclass_fields__)
        unknown = set(payload) - allowed
        if unknown:
            raise WelcomeCardValidationError(f"Unknown field: {sorted(unknown)[0]}")
        values = asdict(cls())
        values.update(payload)
        for key in ("title", "message"):
            if not isinstance(values[key], str) or not values[key].strip():
                raise WelcomeCardValidationError(f"{key} must be a non-empty string.")
            if len(values[key]) > 200:
                raise WelcomeCardValidationError(f"{key} must be 200 characters or fewer.")
        if not isinstance(values["extra_message"], str) or len(values["extra_message"]) > 2_000:
            raise WelcomeCardValidationError("extra_message must be 2,000 characters or fewer.")
        for key in ("accent_color", "text_color"):
            value = values[key]
            if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
                raise WelcomeCardValidationError(f"{key} must be a six-digit hex color.")
            try:
                int(value[1:], 16)
            except ValueError as error:
                raise WelcomeCardValidationError(f"{key} must be a six-digit hex color.") from error
        for key in ("enabled", "show_avatar", "show_member_count"):
            if not isinstance(values[key], bool):
                raise WelcomeCardValidationError(f"{key} must be true or false.")
        channel_id = values["channel_id"]
        if isinstance(channel_id, str) and channel_id.isdigit():
            channel_id = int(channel_id)
            values["channel_id"] = channel_id
        if channel_id is not None and (type(channel_id) is not int or channel_id <= 0):
            raise WelcomeCardValidationError("channel_id must be a positive integer or null.")
        background_url = values["background_url"]
        if background_url is not None:
            if not isinstance(background_url, str) or len(background_url) > 2_000:
                raise WelcomeCardValidationError("background_url is invalid.")
            if not background_url.startswith("https://"):
                raise WelcomeCardValidationError("background_url must use https.")
        return cls(**values)

    def to_dict(self) -> dict:
        result = asdict(self)
        if result["channel_id"] is not None:
            result["channel_id"] = str(result["channel_id"])
        return result
