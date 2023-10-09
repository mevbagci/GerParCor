import dateutil.parser as dparser
from datetime import datetime
import re
import locale
from help_function import save_json, reset_set_files, get_set_files, get_all_path_files
from typing import List

import tqdm


def extract_date_berlin(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{2}.* \d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d. %B %Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_Bremen(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{2}.\d{2}.\d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d.%m.%Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_Bundesrat(file_dir: str):
    try:
        date_time = file_dir.split(" ")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Lichtenstein(file_dir: str):
    try:
        date_time = file_dir.replace("_", ".").split("/")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%Y.%m.%d")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Hessen(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{2}. \d{2}. \d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    text = text.replace(" ", "")
                    date_i = datetime.strptime(text, "%d.%m.%Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_MeckPom(file_dir: str):
    try:
        date_time = file_dir.replace("_.txt", "").split("_")[-1]
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Berlin_Niedersachsen_RheinlandPflaz(file_dir: str):
    counter = 0
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{2}.* \d{4}', line)
            # First date is the issue date not the date where the meeting took place
            if len(text) > 0:
                if counter == 0:
                    counter += 1
                    continue
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d. %B %Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_NRW(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{2}.\d{2}.\d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d.%m.%Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_Saarland_1_3_7(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{2}.* \d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d. %B %Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_Saarland(file_dir: str):
    try:
        date_time = file_dir.replace(".txt", "").split("_")[-1]
        date_i = datetime.strptime(date_time, "%Y-%m-%d")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Thueringen(file_dir: str):
    try:
        date_time = file_dir.replace(".txt", "").split("_")[-1]
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_BadenWuertemmberg(file_dir: str):
    try:
        date_time = file_dir.split(" S.")[0].split(" ")[-1]
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_BadenWuertemmberg_0_8(file_dir: str):
    try:
        date_time = file_dir.split("_")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d%m%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Bayern(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{1}.* \d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d. %B %Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_Brandenburg(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{1}.* \d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d. %B %Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_Sachsen(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{1}.* \d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d. %B %Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None


def extract_date_Hamburg(file_dir: str):
    try:
        date_time = file_dir.split("_")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_SachsenAnhalt(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    with open(file_dir, "r", encoding="utf-8") as txt_file:
        all_line = txt_file.readlines()
        for line in all_line:
            text = re.findall(r'\d{2}.\d{2}.\d{4}', line)
            if len(text) > 0:
                try:
                    text = text[0]
                    date_i = datetime.strptime(text, "%d.%m.%Y")
                    return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
                except:
                    continue
    return None

def extract_date_SchleswigHolstein(file_dir: str):
    try:
        locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
        date_time = file_dir.split(",")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, " %d. %B %Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Wien(file_dir: str):
    try:
        locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
        date_time = file_dir.split("vom ")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d. %B %Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Salzburg(file_dir: str):
    try:
        date_time = file_dir.split("/")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Niederoestereich(file_dir: str):
    try:
        locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
        date_time = file_dir.split("am ")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d. %B %Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None

def extract_date_AustriaNationalrat(file_dir: str):
    try:
        date_time = file_dir.split("_")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Kaernten(file_dir: str):
    try:
        locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
        date_time = file_dir.split("am ")[-1].split(" und")[0].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d. %B %Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None

def extract_date_AustriaBundesrat(file_dir: str):
    try:
        date_time = file_dir.split("_")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None

def extract_date_Steiermark(file_dir: str):
    try:
        locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
        date_time = file_dir.split("vom ")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d.%m.%Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None

def extract_date_TirolSitzung(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
    try:
        date_time = file_dir.split("vom ")[-1].split(" -")[0].split("und ")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d. %B %Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_TirolKurz(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
    try:
        date_time = file_dir.split("vom ")[-1].split(" -")[0].split("und ")[-1].replace(".txt", "")
        date_i = datetime.strptime(date_time, "%d. %B %Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_date_Vorarlberg(file_dir: str):
    locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
    try:
        date_time = file_dir.split("am ")[-1].split("#")[0].split(" -")[0]
        try:
            date_i = datetime.strptime(date_time, "%d.%m.%Y")
        except:
            date_i = datetime.strptime(date_time, "%d. %B %Y")
        return {"year": int(date_i.year), "month": int(date_i.month), "day": int(date_i.day)}
    except:
        return None


def extract_Bundeslaender(list_files: List[str]):
    for file_i in tqdm.tqdm(list_files, desc="Extract date from Files"):
        if "BadenWuertemmberg" in file_i:
            if "/17/" in file_i:
                date_now = extract_date_BadenWuertemmberg(file_i)
            else:
                date_now = extract_date_BadenWuertemmberg_0_8(file_i)
        elif "Bayern" in file_i:
            date_now = extract_date_Bayern(file_i)
        elif "Brandenburg" in file_i:
            date_now = extract_date_Brandenburg(file_i)
        elif "Berlin" in file_i:
            date_now = extract_date_berlin(file_i)
        elif "Austria/Bundesrat" in file_i:
            date_now = extract_date_AustriaBundesrat(file_i)
        elif "Bundesrat" in file_i:
            date_now = extract_date_Bundesrat(file_i)
        elif "Hamburg" in file_i:
            date_now = extract_date_Hamburg(file_i)
        elif "Hessen" in file_i:
            date_now = extract_date_Hessen(file_i)
        elif "Bremen" in file_i:
            date_now = extract_date_Bremen(file_i)
        elif "Liechtenstein" in file_i:
            date_now = extract_date_Lichtenstein(file_i)
        elif "MeckPom" in file_i:
            date_now = extract_date_MeckPom(file_i)
        elif "Niedersachsen" in file_i or "RheinlandPfalz" in file_i:
            date_now = extract_date_Berlin_Niedersachsen_RheinlandPflaz(file_i)
        elif "NordrheinWestfahlen" in file_i:
            date_now = extract_date_NRW(file_i)
        elif "Saarland" in file_i:
            excepts = ["/1/", "/3/", "/7/"]
            if any([x in file_i for x in excepts]):
                date_now = extract_date_Saarland_1_3_7(file_i)
            else:
                date_now = extract_date_Saarland(file_i)
        elif "SachsenAnhalt" in file_i:
            date_now = extract_date_SachsenAnhalt(file_i)
        elif "Sachsen" in file_i:
            date_now = extract_date_Sachsen(file_i)
        elif "SchleswigHolstein" in file_i:
            date_now = extract_date_SchleswigHolstein(file_i)
        elif "Thueringen" in file_i:
            date_now = extract_date_Thueringen(file_i)
        elif "Wien" in file_i:
            date_now = extract_date_Wien(file_i)
        elif "Salzburg" in file_i:
            date_now = extract_date_Salzburg(file_i)
        elif "Niederoestereich" in file_i:
            date_now = extract_date_Niederoestereich(file_i)
        elif "Nationalrat" in file_i:
            date_now = extract_date_AustriaNationalrat(file_i)
        elif "Kaernten" in file_i:
            date_now = extract_date_Kaernten(file_i)
        elif "Steiermark" in file_i:
            date_now = extract_date_Steiermark(file_i)
        elif "Vorarlberg" in file_i:
            date_now = extract_date_Vorarlberg(file_i)
        elif "Tirol/Sitzungsbericht" in file_i:
            date_now = extract_date_TirolSitzung(file_i)
        elif "Tirol/Kurzprotokoll" in file_i:
            date_now = extract_date_TirolKurz(file_i)
        date_out = file_i.replace("/txt/", "/dates/").replace(".txt", ".json")
        if date_now is not None:
            save_json(date_now, date_out)


if __name__ == '__main__':
    bsp = [
        # "/storage/projects/abrami/GerParCor/txt/BadenWuertemmberg/17/Plenarprotokoll 17_1 11.05.2021 S. 1-13.txt",
        # "/storage/projects/abrami/GerParCor/txt/Berlin/18/18_001.txt",
        # "/storage/projects/abrami/GerParCor/txt/Bremen/20/P20L0001.txt",
        # "/storage/projects/abrami/GerParCor/txt/Bundesrat/2021-2025/Plenarprotokoll 999. Sitzung, 18.01.2021.txt",
        # "/storage/projects/abrami/GerParCor/txt/Hessen/19/1.txt",
        # "/storage/projects/abrami/GerParCor/txt/Liechtenstein/2021/2021_1_29.txt",
        # "/storage/projects/abrami/GerParCor/txt/MeckPom/7/7_1_04.10.2016_.txt",
        # "/storage/projects/abrami/GerParCor/txt/Niedersachsen/18/004.txt",
        # "/storage/projects/abrami/GerParCor/txt/NordrheinWestfahlen/17/2.txt",
        # "/storage/projects/abrami/GerParCor/txt/RheinlandPfalz/18/1.txt",
        # "/storage/projects/abrami/GerParCor/txt/Saarland/1/1_1_2023-06-05.txt",
        # "/storage/projects/abrami/GerParCor/txt/Saarland/16/16_5_2017-08-30.txt",
        # "/storage/projects/abrami/GerParCor/txt/Thueringen/6/1_14.10.2014.txt"
        "/storage/projects/abrami/GerParCor/txt/BadenWuertemmberg/8/08_0001_03061980.txt"
    ]
    # extract_Bundeslaender(bsp)
    bd = [
        # "Hessen",
        # "Berlin",
        # "Bremen",
        # "Bundesrat",
        # "Liechtenstein",
        # "MeckPom",
        # "Niedersachsen",
        # "NordrheinWestfahlen",
        # "RheinlandPfalz",
        # "Saarland",
        # "Thueringen",
        # "Bremen",
        # "BadenWuertemmberg/17",
        # "Bayern",
        "Brandenburg",
        # "Bremen,
        # "Hamburg",
        # "Sachsen",
        # "SachsenAnhalt",
        # "SchleswigHolstein"
    ]
    for bd_i in bd:
        reset_set_files()
        get_all_path_files(f"/storage/projects/abrami/GerParCor/txt/Germany/{bd_i}", ".txt")
        all_files = list(get_set_files())
        print(f"Get Date for {bd_i}")
        extract_Bundeslaender(all_files)

    austria = [
        # "Wien",
        # "Salzburg",
        # "Niederoestereich",
        # "Nationalrat",
        # "Kaernten",
        # "Bundesrat",
        # "Steiermark",
        # "Tirol/Sitzungsbericht",
        # "Vorarlberg",
        "Tirol/Kurzprotokoll",
    ]
    # for bd_i in austria:
    #     reset_set_files()
    #     get_all_path_files(f"/storage/projects/abrami/GerParCor/txt/Austria/{bd_i}", ".txt")
    #     all_files = list(get_set_files())
    #     print(f"Get Date for {bd_i}")
    #     extract_Bundeslaender(all_files)
    # BadenW = []
    # for i in range(0, 9):
    #     BadenW.append(f"BadenWuertemmberg/{i}")
    # for bundesland in BadenW:
    #     reset_set_files()
    #     get_all_path_files(f"/storage/projects/abrami/GerParCor/txt/{bundesland}", ".txt")
    #     all_files = list(get_set_files())
    #     print(f"Get Date for {bundesland}")
    #     extract_Bundeslaender(all_files)
