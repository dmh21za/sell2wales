import requests
import datetime

class Searcher:

    def __init__(self):
        pass


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

    from datetime import datetime


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

today = datetime.datetime.now(datetime.timezone.utc)
print(Searcher.has_live_contract('ocds-h6vhtk-05e7e9', today))