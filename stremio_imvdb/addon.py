#!/usr/bin/env python3

import os
from datetime import date
from stremio_imvdb.server import Server
from stremio_imvdb.common import ID_PREFIX, COUNTRIES


config = {
    "host": os.environ.get("STREMIO_IMVDB_HOST", "0.0.0.0"),
    "port": os.environ.get("STREMIO_IMVDB_PORT", "80"),
    "email": os.environ.get("STREMIO_IMVDB_EMAIL", ""),
    "app_key": os.environ.get("STREMIO_IMVDB_APP_KEY", None),
}

if config["app_key"] is None:
    print("STREMIO_IMVDB_APP_KEY environment variable is required")
    exit(1)


MANIFEST = {
    "id": "community.imvdb",
    "version": "0.1.0",
    "name": "IMVDb Music Videos",
    "description": "Watch 83,000+ music videos from IMVDb in Stremio",
    "types": ["Music Videos", "movie"],
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
        {
            "type": "Music Videos",
            "id": "by_country",
            "name": "By Country",
            "extra": [
                {"name": "genre", "isRequired": True, "options": list(COUNTRIES.keys())}
            ],
        },
        {
            "type": "Music Videos",
            "id": "by_year",
            "name": "By Year",
            "extra": [
                {
                    "name": "genre",
                    "isRequired": True,
                    "options": list(range(date.today().year, 1962, -1)),
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


server = Server(MANIFEST, config["app_key"])


def start():
    server.run(host=config["host"], port=config["port"])


if __name__ == "__main__":
    start()
