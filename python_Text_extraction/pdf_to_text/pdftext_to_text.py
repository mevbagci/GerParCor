import pathlib
from typing import Union
import textract
from tqdm import tqdm
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
from multiprocessing import Pool
from functools import partial


def pdf_to_text(pdf_path: str, use_external_source: bool = True) -> bool:
    """
    Converts pdf to txt file
    :param pdf_path:
    :return:
    """
    success = False
    if use_external_source:
        try:
            new_path = os.path.join(PATH, "/".join(pdf_path.split("/")[4:-1])).replace("pdf", "txt")
            if not os.path.exists(os.path.join(new_path, pdf_path.split("/")[-1].replace("pdf", "txt"))):
                pathlib.Path(new_path).mkdir(parents=True, exist_ok=True)
                text = textract.process(pdf_path)
                text = text.decode("utf-8")
                with open(os.path.join(new_path, pdf_path.split("/")[-1].replace("pdf", "txt")), "w") as f:
                    f.write(text)
            success = True
        except Exception as e:
            success = False
            # print(e)
    else:
        try:
            pathlib.Path("/".join(pdf_path.split("/")[:-1])).mkdir(parents=True, exist_ok=True)
            text = textract.process(pdf_path)
            text = text.decode("utf-8")
            with open(pdf_path.replace("pdf", "txt"), "w") as f:
                f.write(text)
            success = True
        except:
            success = False
    return success


def dir_to_txt(dir_path: str) -> [bool]:
    """
    Converts whole pdf directory to txt
    :param dir_path:
    :return:
    """
    files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
    successes = []
    for file in tqdm(files, desc=f"Converting {dir_path.split('/')[-1]}"):
        if ".pdf" in file:
            successes.append(pdf_to_text(file))
        else:
            pass
    return successes


def dir_of_subdirs_to_txt(dir_path: str, forbidden_dirs: Union[list, None]) -> None:
    """
    Converts a whole directory with subdirectories to txt files.
    :param dir_path:
    :param forbidden_dirs:
    :return:
    """
    dir_stack = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
    dir_stack = [file_path for file_path in dir_stack if os.path.isdir(file_path)]
    dir_with_pdf = set()
    while len(dir_stack) != 0:
        dir_path = dir_stack[0]
        sub_elems = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
        sub_files, sub_dirs = [], []
        for elem in sub_elems:
            if os.path.isdir(elem):
                sub_dirs.append(elem)
            elif os.path.isfile(elem):
                sub_files.append(elem)
            else:
                pass
        dir_stack.extend(sub_dirs)
        for sub_file in sub_files:
            if ".pdf" in sub_file:
                dir_with_pdf.add(dir_path)
        dir_stack = dir_stack[1:]
    dir_with_pdf = list(dir_with_pdf)
    # print(dir_with_txt)
    if forbidden_dirs != None:
        for forbidden_dir in forbidden_dirs:
            dir_with_pdf.remove(forbidden_dir)
    pool = Pool(10)
    result = pool.map(dir_to_txt, dir_with_pdf)
    pool.close()
    pool.join()
    successes = []
    for sub_list in result:
        for success in sub_list:
            successes.append(success)
    good, bad = 0, 0
    for success in successes:
        if success:
            good += 1
        else:
            bad += 1
    print(f"Successes: {good}; fails: {bad}")
    return


"""
def convert_path(input_path:str):
    pathlib.Path(new_path).mkdir(parents=True, exist_ok=True)
"""

if __name__ == "__main__":
    input_list = [
        "IX", "V", "VI", "VII", "VIII", "X", "XI", "XIII", "XIV", "XIX", "XV", "XVI", "XVII", "XVIII", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII"
    ]
    kaernten = [
        "27", "28", "29", "30", "31", "32", "33"
    ]
    base_path = f"/storage/projects/abrami/GerParCor/pdf"
    path_kaernten = f"{base_path}/Austria/Kaernten"

    # National_rat
    national_rat = ["XXVII"]
    path_national = f"{base_path}/Austria/Nationalrat"

    # Niederaustria
    niederaustria = [
        "VIII. Gesetzgebungsperiode", "XI. Gesetzgebungsperiode", "XIV. Gesetzgebungsperiode", "XIX. Gesetzgebungsperiode", "XV. Gesetzgebungsperiode", "XVI. Gesetzgebungsperiode", "XVII. Gesetzgebungsperiode",
        "XVIII. Gesetzgebungsperiode", "XX. Gesetzgebungsperiode"
    ]
    path_nieder = f"{base_path}/Austria/Niederoestereich"
    global PATH
    PATH = "/storage/projects/abrami"
    "/storage/projects/abrami/GerParCor/pdf/Austria/Kaernten"
    "/storage/projects/abrami/GerParCor/pdf/Austria/Kaernten"
    # for i_list in input_list:
    #     dir_to_txt(f"/storage/projects/abrami/GerParCor/pdf/Austria/Bundesrat/{i_list}")

    for i_list in kaernten:
        dir_to_txt(f"{path_kaernten}/{i_list}")

    for i_list in national_rat:
        dir_to_txt(f"{path_national}/{i_list}")

    for i_list in niederaustria:
        dir_to_txt(f"{path_nieder}/{i_list}")
    # bd = [
    #       # "Berlin",
    #       # "Bremen",
    #       # "Bundesrat",
    #       # "Liechtenstein",
    #       # "MeckPom",
    #       # "Niedersachsen",
    #       # "NordrheinWestfahlen",
    #       # "RheinlandPfalz",
    #       # "Saarland",
    #       # "Thueringen",
    #       ]
    # for bundesland in bd:
    #     global PATH
    #
    #     dir_of_subdirs_to_txt(f"/storage/projects/abrami/GerParCor/pdf/{bundesland}", [])
