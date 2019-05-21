import aiohttp
import math
from datetime import datetime
from asyncache import cached
from cachetools import TTLCache
from stremio_imvdb.common import ID_PREFIX, SITE_URL, API_URL, COUNTRIES
from stremio_imvdb.parser import IMVDbParser


class IMVDbClient:
    _headers = {"User-Agent": "stremio-imvdb"}

    def __init__(self, app_key):
        self._app_key = app_key

    async def init(self):
        self._parser = IMVDbParser()
        headers = {**self._headers, **{"IMVDB-APP-KEY": self._app_key}}
        self._session = aiohttp.ClientSession(headers=headers)

    async def shutdown(self):
        await self._session.close()

    def _video_to_meta(self, video):
        released = datetime.fromtimestamp(video["release_date_stamp"]).isoformat()
        return {
            "type": "movie",
            "id": ID_PREFIX + str(video["id"]),
            "name": video["song_title"],
            "released": released,
            "releaseInfo": video["year"],
            "inTheaters": False,
            "background": video["image"]["o"],
            "poster": video["image"]["o"],
            "posterShape": "landscape",
            "cast": [artist["name"] for artist in video["artists"]],
            "director": [dir["entity_name"] for dir in video["directors"]],
        }

    @cached(cache=TTLCache(ttl=600, maxsize=1))
    async def get_best_new_list(self):
        async with self._session.get(f"{SITE_URL}/picks") as response:
            text = await response.text()
        return self._parser.parse_rack_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=1))
    async def get_latest_releases_list(self):
        async with self._session.get(f"{SITE_URL}/new") as response:
            text = await response.text()
        return self._parser.parse_rack_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=1))
    async def get_popular_list(self, period):
        period = {
            "Latest": "new",
            "This Week": "week",
            "This Month": "month",
            "All Time": "all",
        }.get(period, "new")
        async with self._session.get(f"{SITE_URL}/charts/{period}") as response:
            text = await response.text()
        return self._parser.parse_chart_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=1))
    async def get_videos_for_country_list(self, country):
        country_code = COUNTRIES[country]
        url = f"{SITE_URL}/country/{country_code}"
        async with self._session.get(url) as response:
            text = await response.text()
        return self._parser.parse_country_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=1))
    async def get_videos_for_year_list(self, year):
        url = f"{SITE_URL}/calendar/{year}"
        async with self._session.get(url) as response:
            text = await response.text()
        return self._parser.parse_year_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=math.inf))
    async def get_video_meta(self, id):
        async with self._session.get(
            f"{API_URL}/video/{id[len(ID_PREFIX):]}?include=sources"
        ) as response:
            video = await response.json()
        return self._video_to_meta(video)

    @cached(cache=TTLCache(ttl=600, maxsize=math.inf))
    async def get_video_streams(self, id):
        async with self._session.get(
            f"{API_URL}/video/{id[len(ID_PREFIX):]}?include=sources"
        ) as response:
            video = await response.json()
        return [
            {"title": "YouTube", "ytId": source["source_data"]}
            for source in video["sources"]
            if source["source"] == "youtube"
        ]
