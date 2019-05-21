![stremio-imvdb](/static/logo_readme.png)

This is a [Stremio](https://www.stremio.com/) add-on with more than 83,000 music videos from __[The Internet Music Video Database](https://imvdb.com/)__.

---

If you just want to watch the videos provided by the add-on in Stremio, you don't need this. Simply open https://stremio-imvdb.schneider.ax and click the install button. Everything below is for running the addon server.

---


## Description

This add-on is a Python app that retrieves the YouTube IDs of music videos from IMVDb and provides them to Stremio. It supports in-memory caching, can be configured using environment variables and run in Docker.

The app has two main parts, add-on server and IMVDb client, both built using [aiohttp](https://aiohttp.readthedocs.io). The server listens for HTTP requests from Stremio clients and dispatches calls to the client, which translates them to requests to the IMVDb API and web interface, parses the responses and caches the results.


## Prerequisites

The minimum version of Python is 3.7, lower versions haven't been tested.

[Poetry](https://poetry.eustace.io/) is used for dependency management, but it isn't required (though recommended), you can instead just use pip.

Additionally, in order for this add-on to work, you will need an IMVDb App Key. To get it, register an app [here](https://imvdb.com/developers/apps/new).


## Installation

First, clone the repo:

```
git clone https://github.com/axtgr/stremio-imvdb
cd stremio-imvdb
```

Then install the dependencies. If you have Poetry:

```
poetry install
```

Otherwise:

```
pip install .
```

If you are planning to change the code, you'll also want to do `pre-commit install` to install the [pre-commit](https://pre-commit.com) git hooks. This way, the code will be linted with [Flake8](http://flake8.pycqa.org) and formatted with [Black](https://black.readthedocs.io) before each commit.


## Environment Variables

Before running the app, set environment variables according to the example for your platform:

#### Linux/OS X

```
export STREMIO_IMVDB_APP_KEY="YOUR_APP_KEY"
```

#### Windows CMD

```
set STREMIO_IMVDB_APP_KEY="YOUR_APP_KEY"
```

#### Windows PowerShell

```
$env:STREMIO_IMVDB_APP_KEY="YOUR_APP_KEY"
```

### List of Variables

Variable                | Default Value     | Description
------------------------| ------------------| ---------------
STREMIO_IMVDB_APP_KEY   |                   | Your IMVDb App Key (required)
STREMIO_IMVDB_HOST      | 0.0.0.0           | Host to listen to
STREMIO_IMVDB_PORT      | 80                | Port to listen to
STREMIO_IMVDB_EMAIL     |                   | Contact email


## Running

Using Poetry:

```
poetry run start
```

Otherwise:

```
python3 stremio_imvdb/addon.py
```

Or, if the above didn't work:

```
python stremio_imvdb/addon.py
```

The add-on will start listening on the specified host and port.


## Known Issues

Even though the add-on provides correct YouTube IDs, Stremio sometimes struggles to load the streams for some unknown reason.


## Screenshot

![Screenshot](/static/screenshot.jpg)


## License

[ISC](LICENSE)
