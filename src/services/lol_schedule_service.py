from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

import aiohttp

SCHEDULE_URL = "https://esports-api.lolesports.com/persisted/gw"
SCHEDULE_PAGE = "https://lolesports.com/en-US/leagues/worlds"
LOCAL_TIMEZONE = ZoneInfo("America/Santiago")
# The public key used by the LoL Esports website, not a Riot Developer API key.
PUBLIC_ESPORTS_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"


class ScheduleUnavailable(Exception):
    pass


@dataclass(frozen=True)
class WorldsMatch:
    id: str
    starts_at: datetime
    teams: tuple[str, str]
    best_of: int
    stage: str
    state: str


class WorldsScheduleService:
    def __init__(self) -> None:
        self._cache: dict[date, tuple[float, list[WorldsMatch]]] = {}
        self._lock = asyncio.Lock()

    async def for_day(self, day: date) -> list[WorldsMatch]:
        async with self._lock:
            cached = self._cache.get(day)
            now = asyncio.get_running_loop().time()
            if cached and now - cached[0] < 300:
                return cached[1]
            matches = await self._fetch(day)
            self._cache[day] = (now, matches)
            return matches

    async def _fetch(self, day: date) -> list[WorldsMatch]:
        headers = {
            "x-api-key": os.getenv("LOL_ESPORTS_API_KEY") or PUBLIC_ESPORTS_KEY,
            "Accept": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                leagues = await self._get(session, "getLeagues", {"hl": "en-US"})
                league = next(
                    (entry for entry in leagues["data"]["leagues"] if entry["slug"] == "worlds"),
                    None,
                )
                if league is None:
                    raise ScheduleUnavailable("Worlds league is absent from the schedule feed")
                league_id = league["id"]
                initial = await self._get(
                    session, "getSchedule", {"hl": "en-US", "leagueId": league_id}
                )
                events = list(initial["data"]["schedule"]["events"])
                pages = initial["data"]["schedule"].get("pages") or {}
                seen: set[str] = set()
                # The default page is centred around current fixtures. Walk both directions
                # so a local-day boundary or a delayed fixture cannot hide a match.
                for direction in ("older", "newer"):
                    token = pages.get(direction)
                    for _ in range(12):
                        if not token or token in seen:
                            break
                        seen.add(token)
                        payload = await self._get(
                            session,
                            "getSchedule",
                            {"hl": "en-US", "leagueId": league_id, "pageToken": token},
                        )
                        schedule = payload["data"]["schedule"]
                        events.extend(schedule["events"])
                        token = (schedule.get("pages") or {}).get(direction)
        except (aiohttp.ClientError, TimeoutError, KeyError, TypeError, ValueError) as exc:
            raise ScheduleUnavailable("Could not read the LoL Esports schedule") from exc

        matches: dict[str, WorldsMatch] = {}
        for event in events:
            if event.get("type") != "match" or event.get("league", {}).get("slug") != "worlds":
                continue
            try:
                starts_at = datetime.fromisoformat(event["startTime"].replace("Z", "+00:00"))
                match = event["match"]
                if starts_at.astimezone(LOCAL_TIMEZONE).date() != day:
                    continue
                teams = match.get("teams") or []
                names = tuple(team.get("name") or "Por definir" for team in teams[:2])
                if len(names) < 2:
                    names = (*names, *("Por definir" for _ in range(2 - len(names))))
                matches[str(match["id"])] = WorldsMatch(
                    id=str(match["id"]),
                    starts_at=starts_at,
                    teams=names,
                    best_of=int((match.get("strategy") or {}).get("count") or 0),
                    stage=event.get("blockName") or "Worlds",
                    state=event.get("state") or "unstarted",
                )
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
        return sorted(matches.values(), key=lambda match: match.starts_at)

    @staticmethod
    async def _get(session: aiohttp.ClientSession, endpoint: str, params: dict) -> dict:
        async with session.get(f"{SCHEDULE_URL}/{endpoint}", params=params) as response:
            response.raise_for_status()
            return await response.json()
