import dateutil.parser as dparser
from datetime import datetime
import re

def extract_date_from_file(file_dir: str):
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.search(r'\d{2}.* \d{4}', line)
            if text is not None:
                print("h")

if __name__ == '__main__':
    extract_date_from_file(f"/storage/projects/abrami/GerParCor/txt/Berlin/18/18_001.txt")
