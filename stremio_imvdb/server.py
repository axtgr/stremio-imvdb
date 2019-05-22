import os
import jinja2
import aiohttp_jinja2
from datetime import date
from aiohttp import web
from stremio_imvdb.client import IMVDbClient


# aiohttp doesn't support route decorators for class methods yet,
# so this is an ad-hoc implementation
# (see https://github.com/aio-libs/aiohttp/pull/3585/)
def route(*args):
    def route_decorator(method):
        method.route_args = args
        return method

    return route_decorator


class Server:
    templates_dir = os.path.dirname(os.path.realpath(__file__)) + "/templates/"

    def __init__(self, manifest, app_key):
        self.manifest = manifest
        self.client = IMVDbClient(app_key=app_key)
        self.app = web.Application()
        self.app.on_response_prepare.append(self.on_response_prepare)
        self.app.on_startup.append(self.on_startup)
        self.app.on_shutdown.append(self.on_shutdown)
        aiohttp_jinja2.setup(
            self.app, loader=jinja2.FileSystemLoader(self.templates_dir)
        )
        routes = [
            web.get(*attr.route_args, getattr(self, key))
            for key, attr in self.__class__.__dict__.items()
            if callable(attr) and hasattr(attr, "route_args")
        ]
        self.app.add_routes(routes)

    async def on_response_prepare(self, request, response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    async def on_startup(self, app):
        await self.client.init()

    async def on_shutdown(self, app):
        await self.client.shutdown()

    @route("/")
    async def home_handler(self, request):
        return aiohttp_jinja2.render_template("home.j2", request, self.manifest)

    @route("/manifest.json")
    async def manifest_handler(self, request):
        return web.json_response(self.manifest)

    @route("/catalog/Music Videos/best_new.json")
    async def best_new_catalog_handler(self, request):
        metas = await self.client.get_best_new_list()
        return web.json_response({"metas": metas})

    @route("/catalog/Music Videos/latest_releases.json")
    async def latest_releases_catalog_handler(self, request):
        metas = await self.client.get_latest_releases_list()
        return web.json_response({"metas": metas})

    @route("/catalog/Music Videos/popular/genre={period}.json")
    async def popular_catalog_handler(self, request):
        period = request.match_info.get("period", "Latest")
        metas = await self.client.get_popular_list(period)
        return web.json_response({"metas": metas})

    @route("/catalog/Music Videos/by_country/genre={country}.json")
    async def by_country_catalog_handler(self, request):
        country = request.match_info.get("country", "United States")
        metas = await self.client.get_videos_for_country_list(country)
        return web.json_response({"metas": metas})

    @route("/catalog/Music Videos/by_year/genre={year}.json")
    async def by_year_catalog_handler(self, request):
        year = request.match_info.get("year", date.today().year)
        metas = await self.client.get_videos_for_year_list(year)
        return web.json_response({"metas": metas})

    @route("/meta/movie/{id}.json")
    async def meta_handler(self, request):
        id = request.match_info["id"]
        meta = await self.client.get_video_meta(id)
        return web.json_response({"meta": meta})

    @route("/stream/movie/{id}.json")
    async def stream_handler(self, request):
        id = request.match_info["id"]
        streams = await self.client.get_video_streams(id)
        return web.json_response({"streams": streams})

    def run(self, *args, **kwargs):
        web.run_app(self.app, *args, **kwargs)
