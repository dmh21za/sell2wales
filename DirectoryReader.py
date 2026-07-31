from Reader import Reader
from pathlib import Path
import pandas as pd

# Reads the whole directory of html files rather than just a single file
class DirectoryReader:

    def __init__(self, dir_loc):
        # Find all html files in the directory

        html_files = [
            str(file)
            for file in Path(dir_loc).glob("*.html")
        ]
        self.html_files = html_files
        self.place_name = dir_loc.split('/')[-1]



    def generate_json_for_all(self):
        print(f"{len(self.html_files)} to read. ")
        for index, file_loc in enumerate(self.html_files):
            r = Reader(file_loc)
            r.generate_json()
            print(f"Done {index + 1} / {len(self.html_files)}.")


    def generate_dataframe(self):
        print(f"{len(self.html_files)} to read.")

        rows = []

        for index, file_loc in enumerate(self.html_files):
            r = Reader(file_loc)

            data = r.parse_html()

            for result in data.get("results", []):
                rows.append({
                    "location": data.get("location"),
                    "date_obtained": data.get("date_obtained"),
                    "page_number": data.get("page_number"),
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "deadline": result.get("deadline")
                })

            print(f"Done {index + 1} / {len(self.html_files)}.")


        df = pd.DataFrame(
            rows,
            columns=[
                "location",
                "date_obtained",
                "page_number",
                "id",
                "title",
                "url",
                "deadline"
            ]
        )

        return df