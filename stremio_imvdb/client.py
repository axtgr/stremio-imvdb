import aiohttp
import math
from datetime import datetime
from asyncache import cached
from cachetools import TTLCache
from stremio_imvdb.common import ID_PREFIX, SITE_URL, API_URL, COUNTRIES
from stremio_imvdb.parser import IMVDbParser


ITEMS_PER_REQUEST = 100


def paginate(items_per_page, skip):
    start_page = math.ceil((skip + 1) / items_per_page)
    start_index = skip % items_per_page
    end_index = start_index + ITEMS_PER_REQUEST
    return {
        "start_page": start_page,
        "start_index": start_index,
        "end_index": end_index,
    }


def paginated(items_per_page):
    def paginated_decorator(method):
        async def paginated_method(*args, skip=0, **kwargs):
            pagination = paginate(items_per_page, skip)
            results = []
            last_results = [None]
            page = pagination["start_page"]

            # Sometimes some results are filtered out, so even if the number of results
            # is lower than items_per_page, it doesn't mean it's the last page.
            while len(last_results) > 0 and len(results) < pagination["end_index"]:
                last_results = await method(*args, page=page)
                results += last_results
                page += 1

            return results[
                pagination["start_index"] : pagination["end_index"]  # noqa: E203
            ]

        return paginated_method

    return paginated_decorator


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
        if video["release_date_stamp"]:
            released = datetime.fromtimestamp(video["release_date_stamp"]).isoformat()
        else:
            released = None

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

    @cached(cache=TTLCache(ttl=600, maxsize=5))
    async def get_best_new_list(self):
        async with self._session.get(f"{SITE_URL}/picks") as response:
            text = await response.text()
        return self._parser.parse_rack_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=5))
    async def get_latest_releases_list(self):
        async with self._session.get(f"{SITE_URL}/new") as response:
            text = await response.text()
        return self._parser.parse_rack_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=100))
    @paginated(40)
    async def get_popular_list(self, period, page=1):
        period = {
            "Latest": "new",
            "This Week": "week",
            "This Month": "month",
            "All Time": "all",
        }.get(period, "new")
        url = f"{SITE_URL}/charts/{period}?page={page}"
        async with self._session.get(url) as response:
            text = await response.text()
        return self._parser.parse_chart_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=100))
    @paginated(50)
    async def get_videos_for_country_list(self, country, page=1):
        country_code = COUNTRIES[country]
        url = f"{SITE_URL}/country/{country_code}?page={page}"
        async with self._session.get(url) as response:
            text = await response.text()
        return self._parser.parse_country_page(text)

    @cached(cache=TTLCache(ttl=600, maxsize=100))
    @paginated(45)
    async def get_videos_for_year_list(self, year, page=1, skip=None):
        url = f"{SITE_URL}/calendar/{year}?page={page}"
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
