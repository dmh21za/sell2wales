
from bs4 import BeautifulSoup
import re
from urllib.parse import parse_qs, urlparse
import json

class Reader:
    def hello():
        print('Hello World')

    def parse_html(self, raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")

        #
        # LOCATION
        #
        location = None

        action = soup.find("form")

        if action and action.has_attr("action"):
            # Example:
            # ./Search_MainPage.aspx?noticeType=1&location=1018
            qs = parse_qs(urlparse(action["action"]).query)

            location_code = qs.get("location", [None])[0]

            if location_code:
                for span in soup.select(
                    "#ctl00_MainBody_pickerLocations_uptPanel span.checkbox"
                ):
                    if span.get("data-value") == location_code:
                        label = span.find("label")
                        if label:
                            location = label.get_text(strip=True)
                        break

        #
        # PAGE DATE
        #
        page_date = None

        # Look for explicit save/generated dates
        for meta in soup.find_all("meta"):
            content = meta.get("content", "")
            m = re.search(r"\d{2}/\d{2}/\d{4}", content)
            if m:
                page_date = m.group()
                break

        # fallback: newest publication date visible on page
        if page_date is None:
            pub_dates = []

            for result in soup.select("div.search-result"):
                for prop in result.select("div.notice-property"):
                    label = prop.select_one("span.notice-refno")

                    if (
                        label
                        and "Publication date" in label.get_text()
                    ):
                        spans = prop.find_all("span")
                        if len(spans) >= 2:
                            pub_dates.append(
                                spans[1].get_text(strip=True)
                            )

            if pub_dates:
                page_date = pub_dates[0]

        #
        # TOTAL RESULTS
        #
        total_results = None

        count_el = soup.select_one("span.results-num")

        if count_el:
            m = re.search(r"\d+", count_el.get_text())
            if m:
                total_results = int(m.group())

        #
        # RESULTS
        #
        results = []

        for notice in soup.select("div.search-result"):

            #
            # title
            #
            title_el = notice.select_one("a.notice-title")
            title = (
                title_el.get_text(" ", strip=True)
                if title_el
                else None
            )

            #
            # id
            #
            notice_id = None

            #
            # deadline
            #
            deadline = None

            for prop in notice.select("div.notice-property"):

                label = prop.select_one("span.notice-refno")

                if not label:
                    continue

                label_text = label.get_text(
                    " ", strip=True
                )

                spans = prop.find_all("span")

                value = (
                    spans[1].get_text(strip=True)
                    if len(spans) > 1
                    else ""
                )

                if "Reference no" in label_text:
                    notice_id = value

                elif "Deadline date" in label_text:
                    deadline = value or None

            results.append(
                (
                    notice_id,
                    title,
                    deadline,
                )
            )

        return (
            location,
            page_date,
            total_results,
            results,
        )
        
        """
        Take location of post
        @html_loc - location of the html file in question
        """

    def __init__(self, html_loc: str):
    
            with open(html_loc, "r", encoding="utf-8") as f:
                raw_html = f.read()
    
            parsed = self.parse_html(raw_html)
    
            with open("test.json", "w", encoding="utf-8") as f:
                json.dump(
                    parsed,
                    f,
                    indent=4,
                    ensure_ascii=False
                )
    
            self.data = parsed

r = Reader('files/swansea/1.html')

print('hello')
    