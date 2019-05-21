import re
from datetime import datetime
from parsel import Selector
from stremio_imvdb.common import ID_PREFIX


class IMVDbParser:
    _regexps = {
        "id_in_poster_url": re.compile("(\\d+)-[^/]*$"),
        "poster_quality": re.compile("_[stbl]v\\.jpg"),
        "title_with_year": re.compile("(.*)\\((\\d{4})\\)"),
    }

    def _parse_poster_url(self, poster_url):
        id = self._regexps["id_in_poster_url"].search(poster_url)
        poster_url = self._regexps["poster_quality"].sub("_ov.jpg", poster_url)
        return poster_url, id and id.group(1)

    def _parse_title_link(self, title_link):
        title = title_link.xpath("./text()").get()
        matches = self._regexps["title_with_year"].search(title)

        if matches:
            return matches.group(1), matches.group(2)
        else:
            return title, ""

    def parse_rack_node(self, item):
        poster, id = self._parse_poster_url(item.css(".rack_img").attrib["src"])
        released_timestamp = int(item.css(".release").attrib["data-release"])
        released = datetime.fromtimestamp(released_timestamp)
        name = self._parse_title_link(item.css("h3 > a"))[0]
        return {
            "type": "movie",
            "id": ID_PREFIX + id,
            "name": name,
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
        name, year = self._parse_title_link(main_td.css("p.artist_line a"))
        return {
            "type": "movie",
            "id": ID_PREFIX + id,
            "name": name,
            "background": poster,
            "poster": poster,
            "posterShape": "landscape",
            "releaseInfo": year,
            "inTheaters": False,
            "cast": [main_td.css("p:nth-child(2) a::text").get()],
            "director": [
                main_td.xpath(
                    ".//p[has-class('node_info')]/em[text() = 'Director:']/following-sibling::a/text()"  # noqa: E501
                ).get()
            ],
        }

    def parse_table_item(self, item):
        poster, id = self._parse_poster_url(
            item.css("td:first-child img").attrib["src"]
        )
        main_td = item.css("td:nth-child(2)")
        name, year = self._parse_title_link(main_td.css("h3 > a"))
        return {
            "type": "movie",
            "id": ID_PREFIX + id,
            "name": name,
            "background": poster,
            "poster": poster,
            "posterShape": "landscape",
            "releaseInfo": year,
            "inTheaters": False,
            "cast": main_td.css("h4 > a::text").getall(),
            "director": [
                item.xpath(
                    ".//td[3]//p[has-class('node_info')]/em[text() = 'Director:']/following-sibling::a/text()"  # noqa: E501
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

    def parse_country_page(self, text):
        page = Selector(text=text)
        return [self.parse_table_item(item) for item in page.css(".imvdbTable tr")]

    def parse_year_page(self, text):
        page = Selector(text=text)
        return [self.parse_table_item(item) for item in page.css(".imvdbTable tr")]
