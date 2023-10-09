import os
import gzip
import json
from tqdm import tqdm


def get_all_path_files(path_dir: str, end_file: str):
    global set_files
    for file in os.scandir(path_dir):
        if file.is_dir():
            get_all_path_files(file, end_file)
        elif (str(file.path)).endswith(f"{end_file}"):
            set_files.add(str(file.path))


def get_set_files():
    global set_files
    return set_files


def save_json(json_data, data_dir, gzip_save=False):
    os.makedirs(os.path.dirname(data_dir), exist_ok=True)
    if gzip_save:
        with gzip.open(data_dir, "wt", encoding="UTF-8") as json_file:
            json.dump(json_data, json_file, indent=2)
    else:
        with open(data_dir, "w", encoding="UTF-8") as json_file:
            json.dump(json_data, json_file, indent=2)


def read_json(data_dir, gzip_load=False):
    if gzip_load:
        with gzip.open(data_dir, "rt", encoding="UTF-8") as json_file:
            return json.load(json_file)
    else:
        with open(data_dir, "r", encoding="UTF-8") as json_file:
            return json.load(json_file)


def reset_set_files():
    global set_files
    set_files = set()


def get_all_not_converted_pdf(path_pdf, path_txt):
    reset_set_files()
    get_all_path_files(path_pdf, ".pdf")
    all_pdf = get_set_files()

    reset_set_files()
    get_all_path_files(path_txt, ".txt")
    all_txt = get_set_files()

    all_failed = []
    for pdf_i in tqdm(all_pdf):
        txt_file_name = pdf_i.replace(".pdf", ".txt").replace("/pdf/", "/txt/")
        if txt_file_name not in all_txt:
            all_failed.append(pdf_i)
    all_failed.sort()
    return all_failed


if __name__ == '__main__':
    germany = [
        "BadenWuertemmberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Bundesrat", "Hamburg", "Hessen", "MeckPom",
        "Niedersachsen", "NordrheinWestfahlen", "RheinlandPfalz", "Saarland", "Sachsen", "SachsenAnhalt", "SchleswigHolstein",
        "Thueringen"
    ]
    lichtenstein = [
        2021, 2022, 2023
    ]
    austria = [
        "Bundesrat", "Kaernten", "Nationalrat", "Niederoestereich", "Salzburg", "Steiermark", "Wien", "Tirol", "Vorarlberg"
    ]
    germany_failed = {}
    lichtenstein_failed = {}
    austria_failed = {}
    for bundesland in germany:
        germany_failed[bundesland] = get_all_not_converted_pdf(f"/storage/projects/abrami/GerParCor/pdf/Germany/{bundesland}", f"/storage/projects/abrami/GerParCor/txt/Germany/{bundesland}")
        path_i =f"/storage/projects/abrami/GerParCor/failed/Germany/{bundesland}.json"
        save_json(germany_failed[bundesland], path_i)
    path_i = f"/storage/projects/abrami/GerParCor/failed/Germany/all.json"
    save_json(germany_failed, path_i)

    for bundesland in austria:
        austria_failed[bundesland] = get_all_not_converted_pdf(f"/storage/projects/abrami/GerParCor/pdf/Austria/{bundesland}", f"/storage/projects/abrami/GerParCor/txt/Austria/{bundesland}")
        path_i =f"/storage/projects/abrami/GerParCor/failed/Austria/{bundesland}.json"
        save_json(austria_failed[bundesland], path_i)
    path_i = f"/storage/projects/abrami/GerParCor/failed/Austria/all.json"
    save_json(austria_failed, path_i)