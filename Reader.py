
from bs4 import BeautifulSoup
import re
from urllib.parse import parse_qs, urlparse, urljoin
import json
from datetime import datetime


class Reader:
    def hello():
        print('Hello World')

    def parse_html(self):
        soup = BeautifulSoup(
            self.raw_html,
            "html.parser"
        )

        #
        # LOCATION
        #
        location = None

        form = soup.find("form")

        if form and form.has_attr("action"):

            query_string = parse_qs(
                urlparse(form["action"]).query
            )

            location_code = query_string.get(
                "location",
                [None]
            )[0]

            if location_code:

                for span in soup.select(
                    "#ctl00_MainBody_pickerLocations_uptPanel span.checkbox"
                ):

                    if span.get("data-value") == location_code:

                        label = span.find("label")

                        if label:
                            location = (
                                label.get_text(strip=True)
                                .lstrip(". ")
                                .strip()
                            )

                        break

        #
        # TOTAL RESULTS
        #
        total_results = None

        results_num = soup.select_one(
            "span.results-num"
        )

        if results_num:

            match = re.search(
                r"\d+",
                results_num.get_text()
            )

            if match:
                total_results = int(
                    match.group()
                )

        #
        # RESULTS
        #
        results = []

        for notice in soup.select(
            "div.search-result"
        ):

            title_el = notice.select_one(
                "a.notice-title"
            )

            if not title_el:
                continue

            title = title_el.get_text(
                " ",
                strip=True
            )

            url = urljoin(
                "https://www.sell2wales.gov.wales/",
                title_el.get("href", "")
            )

            #
            # All properties
            #
            props = {}

            for prop in notice.select(
                "div.notice-property"
            ):

                spans = prop.find_all("span")

                if len(spans) < 2:
                    continue

                key = (
                    spans[0]
                    .get_text(" ", strip=True)
                    .rstrip(":")
                    .strip()
                )

                value = (
                    spans[1]
                    .get_text(" ", strip=True)
                    .strip()
                )

                props[key] = value

            results.append(
                {
                    "id": props.get(
                        "Reference no"
                    ),
                    "ocid": props.get(
                        "OCID"
                    ),
                    "date_obtained": self.page_date,
                    "title": title,
                    "url": url,
                    "deadline": props.get(
                        "Deadline date"
                    ),
                    "publication_date": props.get(
                        "Publication date"
                    ),
                    "notice_type": props.get(
                        "Notice Type"
                    ),
                    "published_by": props.get(
                        "Published by"
                    ),
                    "value": props.get(
                        "Value"
                    )
                }
            )

        return {
            "location": location,
            "date_obtained": self.page_date,
            "total_results": total_results,
            "page_number": self.page_number,
            "results": results
        }

    def generate_json(self):
        parsed = self.parse_html()

        filename = f"{self.html_loc.split('.', 2)[0]}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                parsed,
                f,
                indent=4,
                ensure_ascii=False
            )

        self.data = parsed

    def __init__(self, html_loc: str):

        with open(html_loc, "r", encoding="utf-8") as f:
            self.raw_html = f.read()

        self.page_number = html_loc.split('/')[-1].split('.html', 2)[0]
        self.html_loc = html_loc
        self.page_date = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

r = Reader('files/swansea/1.html')
r.parse_html()