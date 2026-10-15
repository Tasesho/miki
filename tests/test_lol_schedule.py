from datetime import date, datetime
from types import SimpleNamespace

import pytest

from modules.lol_schedule import LolSchedule, schedule_embed
from services.lol_schedule_service import LOCAL_TIMEZONE, WorldsMatch, WorldsScheduleService


@pytest.mark.asyncio
async def test_worlds_matches_use_santiago_day_and_all_pages(monkeypatch):
    calls = []

    async def fake_get(session, endpoint, params):
        calls.append((endpoint, params.copy()))
        if endpoint == "getLeagues":
            return {"data": {"leagues": [{"slug": "worlds", "id": "worlds-id"}]}}
        token = params.get("pageToken")
        if token == "next":
            return {
                "data": {
                    "schedule": {
                        "events": [
                            {
                                "type": "match",
                                "league": {"slug": "worlds"},
                                "startTime": "2026-10-16T02:30:00Z",
                                "blockName": "Play-In",
                                "state": "unstarted",
                                "match": {
                                    "id": "2",
                                    "teams": [{"name": "Cloud9"}, {"name": "FURIA"}],
                                    "strategy": {"count": 5},
                                },
                            }
                        ],
                        "pages": {},
                    }
                }
            }
        return {
            "data": {
                "schedule": {
                    "events": [
                        {
                            "type": "match",
                            "league": {"slug": "worlds"},
                            "startTime": "2026-10-15T20:00:00Z",
                            "blockName": "Play-In",
                            "state": "unstarted",
                            "match": {
                                "id": "1",
                                "teams": [{"name": "Cloud9"}, {"name": "Karmine Corp"}],
                                "strategy": {"count": 5},
                            },
                        },
                        {
                            "type": "match",
                            "league": {"slug": "lck"},
                            "startTime": "2026-10-15T20:00:00Z",
                            "match": {"id": "3"},
                        },
                    ],
                    "pages": {"newer": "next"},
                }
            }
        }

    monkeypatch.setattr(WorldsScheduleService, "_get", staticmethod(fake_get))
    service = WorldsScheduleService()
    matches = await service.for_day(date(2026, 10, 15))

    assert [match.id for match in matches] == ["1", "2"]
    assert all(
        match.starts_at.astimezone(LOCAL_TIMEZONE).date() == date(2026, 10, 15) for match in matches
    )
    assert len(schedule_embed(date(2026, 10, 15), matches).fields) == 2
    assert len(calls) == 3
    assert await service.for_day(date(2026, 10, 15)) == matches
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_daily_announcement_is_sent_once(monkeypatch):
    class FixedDateTime:
        @staticmethod
        def now(timezone):
            return datetime(2026, 10, 15, 12, 5, tzinfo=timezone)

    class Settings:
        values = {"lol_schedule_enabled": "1", "lol_schedule_last_sent_date": None}

        async def get(self, guild_id, key):
            return self.values[key]

        async def get_int(self, guild_id, key):
            return 42

        async def set(self, guild_id, key, value):
            self.values[key] = value

    class Channel:
        sent = []

        def permissions_for(self, member):
            return SimpleNamespace(view_channel=True, send_messages=True, embed_links=True)

        async def send(self, **kwargs):
            self.sent.append(kwargs)

    class Schedule:
        async def for_day(self, day):
            return [
                WorldsMatch(
                    id="1",
                    starts_at=datetime(2026, 10, 15, 15, tzinfo=LOCAL_TIMEZONE),
                    teams=("Cloud9", "Karmine Corp"),
                    best_of=5,
                    stage="Play-In",
                    state="unstarted",
                )
            ]

    monkeypatch.setattr("modules.lol_schedule.datetime", FixedDateTime)
    channel = Channel()
    guild = SimpleNamespace(id=1, me=object(), get_channel=lambda channel_id: channel)
    cog = LolSchedule.__new__(LolSchedule)
    cog.bot = SimpleNamespace(guilds=[guild])
    cog.settings = Settings()
    cog.schedule = Schedule()

    await LolSchedule.daily_post.coro(cog)
    await LolSchedule.daily_post.coro(cog)

    assert len(channel.sent) == 1
    assert cog.settings.values["lol_schedule_last_sent_date"] == "2026-10-15"
