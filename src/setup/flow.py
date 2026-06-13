from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SetupFlow:
    key: str
    title: str
    description: str


@dataclass
class SetupSession:
    guild_id: int
    flow_key: str
    state: dict[str, Any] = field(default_factory=dict)

    def set_value(self, key: str, value: Any) -> None:
        self.state[key] = value

    def get_value(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
