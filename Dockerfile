FROM python:3.7

LABEL maintainer="me@schneider.ax"

WORKDIR /var/www/imvdb
EXPOSE 80

COPY ./pyproject.toml /var/www/imvdb/pyproject.toml
COPY ./stremio_imvdb /var/www/imvdb/stremio_imvdb
RUN pip install .

CMD python3 stremio_imvdb/addon.py
