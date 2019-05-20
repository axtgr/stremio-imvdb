![stremio-imvdb](/static/logo_readme.png)

This is a [Stremio](https://www.stremio.com/) add-on with more than 83,000 music videos from __[The Internet Music Video Database](https://imvdb.com/)__.

---

If you just want to watch the videos provided by the add-on in Stremio, open https://stremio-imvdb.schneider.ax and click the install button. Everything below is for running the addon server.

---


## Description

This is a Python app that retrieves the YouTube IDs of music videos from IMVDb using both its API and web interface and provides them to Stremio. It supports in-memory caching, can be configured using environment variables and run in Docker.


## App Registration

In order for this add-on to work, you need to provide an IMVDb App Key. To get it, register an app [here](https://imvdb.com/developers/apps/new).


## Installation

First, clone the repo:

```
git clone https://github.com/axtgr/stremio-imvdb
cd stremio-imvdb
```

The add-on uses [Poetry](https://github.com/sdispater/poetry) for dependency management. If you already have Poetry, you can use it to install the dependencies:

```
poetry install
```

Otherwise, you can simply use pip:

```
pip install .
```


## Environment Variables

Before running the app, set environment variables as follows:

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

If you have Poetry:

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

![Screenshot](/static/screenshot.png)


## License

[ISC](LICENSE)
