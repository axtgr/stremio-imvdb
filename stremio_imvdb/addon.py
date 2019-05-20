#!/usr/bin/env python3

import os
import jinja2
import aiohttp_jinja2
from aiohttp import web
from .client import IMVDbClient
from .common import ID_PREFIX


config = {
    "host": os.environ.get("STREMIO_IMVDB_HOST", "0.0.0.0"),
    "port": os.environ.get("STREMIO_IMVDB_PORT", "80"),
    "email": os.environ.get("STREMIO_IMVDB_EMAIL", ""),
    "app_key": os.environ.get("STREMIO_IMVDB_APP_KEY", None),
}

if config["app_key"] is None:
    print("STREMIO_IMVDB_APP_KEY environment variable is required")
    exit(1)


TEMPLATES_DIR = os.path.dirname(os.path.realpath(__file__)) + "/templates/"
MANIFEST = {
    "id": "community.imvdb",
    "version": "0.1.0",
    "name": "IMVDb Music Videos",
    "description": "Watch 83,000+ music videos from IMVDb in Stremio",
    "types": ["movie"],
    "catalogs": [
        {"type": "Music Videos", "id": "best_new", "name": "Best New"},
        {"type": "Music Videos", "id": "latest_releases", "name": "Latest Releases"},
        {
            "type": "Music Videos",
            "id": "popular",
            "name": "Popular",
            "extra": [
                {
                    "name": "genre",
                    "isRequired": True,
                    "options": ["Latest", "This Week", "This Month", "All Time"],
                }
            ],
        },
    ],
    "resources": [
        "catalog",
        {"name": "meta", "types": ["movie"], "idPrefixes": [ID_PREFIX]},
        {"name": "stream", "types": ["movie"], "idPrefixes": [ID_PREFIX]},
    ],
    "contactEmail": config["email"],
    "logo": "https://github.com/axtgr/stremio-imvdb/blob/master/static/logo.png?raw=true",  # noqa: E501
    "background": "https://github.com/axtgr/stremio-imvdb/blob/master/static/background.jpg?raw=true",  # noqa: E501
}


client = IMVDbClient(app_key=config["app_key"])
routes = web.RouteTableDef()


@routes.get("/")
@aiohttp_jinja2.template("home.j2")
async def home_handler(request):
    return MANIFEST


@routes.get("/manifest.json")
async def manifest_handler(request):
    return web.json_response(MANIFEST)


@routes.get("/catalog/Music Videos/best_new.json")
async def best_new_catalog_handler(request):
    metas = await client.get_best_new_list()
    return web.json_response({"metas": metas})


@routes.get("/catalog/Music Videos/latest_releases.json")
async def latest_releases_catalog_handler(request):
    metas = await client.get_latest_releases_list()
    return web.json_response({"metas": metas})


@routes.get("/catalog/Music Videos/popular.json")
@routes.get("/catalog/Music Videos/popular/genre={period}.json")
async def popular_catalog_handler(request):
    period = request.match_info.get("period", "Latest")
    metas = await client.get_popular_list(period)
    return web.json_response({"metas": metas})


@routes.get("/meta/movie/{id}.json")
async def meta_handler(request):
    id = request.match_info["id"]
    meta = await client.get_video_meta(id)
    return web.json_response({"meta": meta})


@routes.get("/stream/movie/{id}.json")
async def stream_handler(request):
    id = request.match_info["id"]
    streams = await client.get_video_streams(id)
    return web.json_response({"streams": streams})


@routes.get("/{path:.*}")
async def default_handler(request):
    print("Unknown request:", request.url)
    raise web.HTTPNotFound


async def on_response_prepare(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def on_startup(app):
    await client.init()


async def on_shutdown(app):
    await client.shutdown()


app = web.Application()
app.on_response_prepare.append(on_response_prepare)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.add_routes(routes)
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES_DIR))


def start():
    web.run_app(app, host=config["host"], port=config["port"])


if __name__ == "__main__":
    start()
