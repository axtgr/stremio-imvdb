import re
from datetime import datetime
from parsel import Selector
from stremio_imvdb.common import ID_PREFIX


class IMVDbParser:
    _regexps = {
        "id_in_poster_url": re.compile("(\\d+)-[^/]*$"),
        "poster_quality": re.compile("_[stbl]v\\.jpg"),
    }

    def _parse_poster_url(self, poster_url):
        id = self._regexps["id_in_poster_url"].search(poster_url)
        poster_url = self._regexps["poster_quality"].sub("_ov.jpg", poster_url)
        return poster_url, id and id.group(1)

    def parse_rack_node(self, item):
        poster, id = self._parse_poster_url(item.css(".rack_img").attrib["src"])
        released_timestamp = int(item.css(".release").attrib["data-release"])
        released = datetime.fromtimestamp(released_timestamp)
        return {
            "type": "movie",
            "id": ID_PREFIX + id,
            "name": item.css("h3 > a").attrib["title"],
            "released": released.isoformat(),
            "releaseInfo": released.year,
            "inTheaters": False,
            "background": poster,
            "poster": poster,
            "posterShape": "landscape",
            "cast": [item.css("h4 > a::text").get()],
            "director": [
                item.xpath(
                    ".//*[has-class('node_info')]/em[text() = 'dir:']/following-sibling::a/text()"  # noqa: E501
                ).get()
            ],
        }

    def parse_chart_item(self, item):
        poster, id = self._parse_poster_url(
            item.css("td:first-child img").attrib["src"]
        )
        main_td = item.css("td:nth-child(2)")
        return {
            "type": "movie",
            "id": ID_PREFIX + id,
            "name": main_td.css("p.artist_line a").attrib["title"],
            "background": poster,
            "poster": poster,
            "posterShape": "landscape",
            "inTheaters": False,
            "cast": [main_td.css("p:nth-child(2) a::text").get()],
            "director": [
                main_td.xpath(
                    ".//p[has-class('node_info')]/em[text() = 'Director:']/following-sibling::a/text()"  # noqa: E501
                ).get()
            ],
        }

    def parse_rack_page(self, text):
        page = Selector(text=text)
        return [self.parse_rack_node(item) for item in page.css(".rack_node")]

    def parse_chart_page(self, text):
        page = Selector(text=text)
        return [
            self.parse_chart_item(item) for item in page.css(".imvdb-chart-table tr")
        ]
