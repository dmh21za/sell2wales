import requests
import datetime
import time
import requests
from functools import lru_cache
import json

class Searcher:

    def __init__(self):
        pass


    @staticmethod
    @lru_cache(maxsize=None)
    def search(ocid: str) -> dict:
        """
        Retrieve a Find a Tender OCDS release package by OCID.

        Returns the parsed JSON response as a Python dict.
        Raises requests.HTTPError if the request fails.
        """

        url = (
            f"https://www.find-tender.service.gov.uk/"
            f"api/1.0/ocdsReleasePackages/{ocid}"
        )

        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=30,
        )

        response.raise_for_status()

        return response.json()


    @staticmethod
    def generate_ocid_latest_contract_dict(
        ocids: list[str]
    ) -> dict[str, datetime.datetime | None]:

        results = {}

        #
        # Deduplicate while preserving order
        #
        unique_ocids = list(dict.fromkeys(
            ocid
            for ocid in ocids
            if ocid
        ))

        counter = 0
        for ocid in unique_ocids:

            while True:

                try:
                    data = Searcher.search(ocid)

                    latest_deadline = None

                    for release in data.get(
                        "releases",
                        []
                    ):

                        for contract in release.get(
                            "contracts",
                            []
                        ):

                            period = contract.get(
                                "period",
                                {}
                            )

                            end_date = period.get(
                                "endDate"
                            )

                            if not end_date:
                                continue

                            deadline = (
                                datetime.datetime
                                .fromisoformat(
                                    end_date.replace(
                                        "Z",
                                        "+00:00"
                                    )
                                )
                            )

                            if (
                                latest_deadline is None
                                or deadline > latest_deadline
                            ):
                                latest_deadline = deadline

                    results[ocid] = latest_deadline
                    counter += 1
                    print(f"Done {counter} / {len(unique_ocids)}")

                    break

                except requests.HTTPError as e:

                    if (
                        e.response is not None
                        and e.response.status_code == 429
                    ):

                        retry_after = int(
                            e.response.headers.get(
                                "Retry-After",
                                10
                            )
                        )

                        print(
                            f"Rate limited. "
                            f"Waiting {retry_after}s "
                            f"for {ocid}"
                        )

                        time.sleep(retry_after)

                        continue
                    elif e.response is not None:   
                        results[ocid] = str(e.response.status_code)
                        counter += 1
                        break

                    raise

        return results



    @staticmethod
    def save_ocid_latest_contract_dict(
        ocids,
        file_loc: str
    ) -> dict:

        contract_dict = (
            Searcher.generate_ocid_latest_contract_dict(
                ocids
            )
        )

        #
        # Convert datetimes to ISO strings
        #

        serializable = {}

        for ocid, deadline in contract_dict.items():

            if isinstance(deadline, datetime.datetime):
                serializable[ocid] = deadline.strftime(
                    "%Y-%m-%d"
                )

            else:
                serializable[ocid] = deadline


        with open(
            file_loc,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                serializable,
                f,
                indent=4,
                ensure_ascii=False
            )

        return serializable


    def has_live_contract(ocid: str, date: datetime) -> bool:
        data = Searcher.search(ocid)
            
        for release in data.get("releases", []):
            for contract in release.get("contracts", []):

                if contract.get("status") != "active":
                    continue

                period = contract.get("period", {})
                end_date = period.get("endDate")

                if not end_date:
                    continue

                contract_end = datetime.datetime.fromisoformat(
                    end_date.replace("Z", "+00:00")
                )

                if contract_end > date:
                    return True

        return False

# today = datetime.datetime.now(datetime.timezone.utc)
# print(Searcher.has_live_contract('ocds-h6vhtk-05e7e9', today))