from __future__ import annotations

import random
from dataclasses import dataclass

import aiohttp


@dataclass(frozen=True)
class WeatherResult:
    city: str
    country: str
    temperature_c: float
    feels_like_c: float
    humidity: int
    condition: str
    icon_url: str


class WeatherClient:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1/current.json"

    async def current(self, city: str, country: str = "Chile") -> WeatherResult | None:
        if not self.api_key:
            return None

        params = {"key": self.api_key, "q": f"{city},{country}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params, timeout=10) as response:
                if response.status != 200:
                    return None
                data = await response.json()

        condition = data["current"]["condition"]
        return WeatherResult(
            city=data["location"]["name"],
            country=data["location"]["country"],
            temperature_c=data["current"]["temp_c"],
            feels_like_c=data["current"]["feelslike_c"],
            humidity=data["current"]["humidity"],
            condition=condition["text"],
            icon_url=f"https:{condition['icon']}",
        )


class GifClient:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.base_url = "https://api.giphy.com/v1/gifs/search"

    async def random_gif_url(self, query: str) -> str | None:
        if not self.api_key:
            return None

        params = {"api_key": self.api_key, "q": query, "limit": 10, "lang": "es"}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params, timeout=10) as response:
                if response.status != 200:
                    return None
                data = await response.json()

        gifs = data.get("data", [])
        if not gifs:
            return None
        return random.choice(gifs)["images"]["original"]["url"]
