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
        # "VIII. Gesetzgebungsperiode", "XI. Gesetzgebungsperiode", "XIV. Gesetzgebungsperiode", "XIX. Gesetzgebungsperiode", "XV. Gesetzgebungsperiode", "XVI. Gesetzgebungsperiode", "XVII. Gesetzgebungsperiode",
        # "XVIII. Gesetzgebungsperiode",
        "XX. Gesetzgebungsperiode"
    ]
    path_nieder = f"{base_path}/Austria/Niederoestereich"

    #Salzburg
    salzburg = [
        "11", "12", "13", "14", "15", "16"
    ]
    path_salzburg = f"{base_path}/Austria/Salzburg"


    #Steiermark
    path_steiermark = f"{base_path}/Austria/Steiermark"
    steiermark = [
        "1945 - 1949 (Periode I)", "1949 - 1953 (Periode II)", "1953 - 1957 (Periode III)", "1957 - 1961 (Periode IV)", "1961 - 1965 (Periode V)", "1965 - 1970 (Periode VI)"
    ]

    #Wien
    path_wien = f"{base_path}/Austria/Wien"
    wien = list(range(1998, 2024))
    global PATH
    PATH = "/storage/projects/abrami"

    # #Bayern
    # path_bayern = f"{base_path}/Germany/Bayern"
    # bayern = [18]
    # for i_list in bayern:
    #     dir_to_txt(f"{path_bayern}/{i_list}")
    #
    # #Brandenburg
    # path_brandenburg = f"{base_path}/Germany/Brandenburg"
    # brandenburg = [7]
    # for i_list in brandenburg:
    #     dir_to_txt(f"{path_brandenburg}/{i_list}")
    #
    # #Hamburg
    # path_hamburg = f"{base_path}/Germany/Hamburg"
    # hamburg = [22]
    # for i_list in hamburg:
    #     dir_to_txt(f"{path_hamburg}/{i_list}")
    #
    # #MeckPom
    # path_meckpom = f"{base_path}/Germany/MeckPom"
    # meckpom = [8]
    # for i_list in meckpom:
    #     dir_to_txt(f"{path_meckpom}/{i_list}")
    #
    # #Sachsen
    # path_sachsen = f"{base_path}/Germany/Sachsen"
    # sachsen = [7]
    # for i_list in sachsen:
    #     dir_to_txt(f"{path_sachsen}/{i_list}")
    #
    # # SachsenAnhalt
    # path_sachsenanhalt = f"{base_path}/Germany/SachsenAnhalt"
    # sachsenanhalt = [8]
    # for i_list in sachsenanhalt:
    #     dir_to_txt(f"{path_sachsenanhalt}/{i_list}")
    #
    # #SchleswigHolstein
    # path_schleswig = f"{base_path}/Germany/SchleswigHolstein"
    # schleswigholstein = [19, 20]
    # for i_list in schleswigholstein:
    #     dir_to_txt(f"{path_schleswig}/{i_list}")
    #
    # #Bundesrat Austria
    # path_bundesrat = f"{base_path}/Austria/Bundesrat"
    # bundesrat = ["XII"]
    # for i_list in bundesrat:
    #     dir_to_txt(f"{path_bundesrat}/{i_list}")

    #voralberg
    # path_vorarlberg = f"/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg"
    # vorarlberg = [
    #     1861, 1863, 1864, 1868, 1870, 1871, 1881, 1882, 1883, 1884, 1885, 1886, 1888, 1889, 1890, 1892, 1893,
    #     1894, 1896, 1897, 1899, 1900, 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1913, 1928, 1929, 1933,
    #     1934, 1935, 1936, 1965, 1966, 1967, 1968, 1969, 1972, 1973, 1974, 1984, 1985, 1986
    # ]
    # for i_list in vorarlberg:
    #     dir_to_txt(f"{path_vorarlberg}/{i_list}")

    #
    # path_nieder2 = f"/storage/projects/abrami/GerParCor/pdf/Austria/Niederoestereich/VIII. Gesetzgebungsperiode/4. Session – 11. Landtagssitzung"
    # dir_to_txt(path_nieder2)

    # for i_list in input_list:
    #     dir_to_txt(f"/storage/projects/abrami/GerParCor/pdf/Austria/Bundesrat/{i_list}")

    # for i_list in kaernten:
    #     dir_to_txt(f"{path_kaernten}/{i_list}")
    #
    # for i_list in national_rat:
    #     dir_to_txt(f"{path_national}/{i_list}")
    #
    # for i_list in niederaustria:
    #     dir_to_txt(f"{path_nieder}/{i_list}")

    # for i_list in salzburg:
    #     dir_to_txt(f"{path_salzburg}/{i_list}")
    #
    # for i_list in steiermark:
    #     dir_to_txt(f"{path_steiermark}/{i_list}")
    #
    # for i_list in wien:
    #     dir_to_txt(f"{path_wien}/{i_list}")
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

    # tirol = list(range(1970, 2024))
    # path_tirol = f"{base_path}/Austria/Tirol/Sitzungsbericht"
    # # out_tirol = f"{out_base}/Austria/Tirol/Sitzungsbericht"
    # for i in tirol:
    #     input_path = f"{path_tirol}/{i} Periode"
    #     if os.path.exists(input_path):
    #         dir_to_txt(input_path)
    #
    # tirol_kurz = list(range(1946, 2024))
    # path_tirol_kurz = f"{base_path}/Austria/Tirol/Kurzprotokoll"
    # # out_tirol_kurz = f"{out_base}/Austria/Tirol/Kurzprotokoll"
    # for i in tirol_kurz:
    #     input_path = f"{path_tirol_kurz}/{i} Periode"
    #     if os.path.exists(input_path):
    #         dir_to_txt(input_path)

    #vorarlberg
    # vorarlberg = ["1887"]
    # path_vorarlberg = f"{base_path}/Austria/Vorarlberg"
    # for i in vorarlberg:
    #     input_path = f"{path_vorarlberg}/{i}"
    #     # os.makedirs(input_path, exist_ok=True)
    #     # os.path.exists(input_path, exist)
    #     dir_to_txt(input_path)

    # path_ober = f"{base_path}/Austria/Oberoestereich"
    # out_ober = f"{base_path}/Austria/Oberoestereich"
    # oberautria = [
    #               # "XXIX", "XXVI",
    #               "XXVII", "XXVIII"
    #               ]
    # for i in oberautria:
    #     input_path = f"{path_ober}/{i}._Gesetzgebungsperiode"
    #     # os.makedirs(input_path, exist_ok=True)
    #     # os.path.exists(input_path, exist)
    #     if os.path.exists(input_path):
    #         dir_to_txt(input_path)
    #     else:
    #         input_path = f"{path_ober}/{i}. Gesetzgebungsperiode"
    #         dir_to_txt(input_path)

    path_vorarlberg = f"{base_path}/Austria/Vorarlberg_test4"
    out_vorarlberg = f"{base_path}/Austria/Vorarlberg_test4"
    vorarlberg = {
        "31. Landtagsperiode (6. November 2019 - 5. November 2024)": [2021, 2020, 2019],
        "30. Landtagsperiode (15. Oktober 2014 - 5. November 2019)": list(range(2014, 2020)),
        "29. Landtagsperiode (Oktober 2009 - September 2014)": list(range(2009, 2015)),
        "28. Landtag (Oktober 2004 - September 2009)": list(range(2004, 2010)),
        "27. Landtag (September 1999 - September 2004)": list(range(1999, 2005)),
        "26. Landtag (September 1994 - September 1999)": list(range(1994, 2000))+[0],
        "25. Landtag (Oktober 1989 - September 1994)": list(range(1989, 1995))+["(Not Categorized)"],
        "24. Landtag (Oktober 1984 - September 1989)": list(range(2004, 2010))+["(Not Categorized)"],
        "23. Landtag (November 1979 bis September 1984)": list(range(1979, 1985)),
        "22. Landtag (November 1974 - Juli 1979)": list(range(1974, 1980)),
        "21. Landtag (Oktober 1969 - Juli 1974)": list(range(1969, 1975))+["(Not Categorized)"],
        "20. Landtag (Oktober 1964 - Juli 1969)": list(range(1964, 1970)),
        "19. Landtag (Oktober 1959 - Oktober 1964)": list(range(1959, 1965)),
        "18. Landtag (Oktober 1954 - Dezember 1958)": list(range(1954, 1959)),
        "17. Landtag (Oktober 1949 - Juli 1954)": list(range(1949, 1955)),
        "16. Landtag (November 1945 - September 1949)": list(range(1945, 1950)),
        "15. Landtag (November 1934 - Dezember 1937)": list(range(1934, 1938)),
        "14. Landtag (November 1932 - Oktober 1934)": list(range(1932, 1935)),
        "13. Landtag (April 1928 - September 1932)": list(range(1928, 1933)),
        "12. Landtag (6.11.1923 - 2.2.1928)": list(range(1923, 1929)),
        "11. Landtag (17.6.1919 - 10.9.1923)": list(range(1919, 1924))+["(Not Categorized)"],
        "10. Landtag (16.9.1909 - 4.6.1914)": list(range(1909, 1915))+["(Not Categorized)"],
        "09. Landtag (22.12.1902 - 17.10.1908)": list(range(1902, 1909)),
        "08. Landtag (26.1.1897 - 17.7.1902)": list(range(1897, 1903)),
        "07. Landtag (14.10.1890-05.02.1896)": list(range(1890, 1897)),
        "07. Landtag (14.10.1890 - 05.02.1896)": list(range(1890, 1897)),
        "06. Landtag (11.08.1884 - 30.10.1889)":  list(range(1884, 1890)),
        "05. Landtag (24.09.1878 - 13.08.1883)":  list(range(1878, 1884)),
        "04. Landtag (18.12.1871-21.04.1877)":  list(range(1871, 1878)),
        "04. Landtag (18.12.1871 - 21.04.1877)":  list(range(1871, 1878))+["(Not Categorized)"],
        "03. Landtag (20.08.1870 - 14.10.1871)":  list(range(1870, 1872)),
        "02. Landtag (18.02.1867 - 30.10.1869)":  list(range(1867, 1870)),
        "01. Landtag (04.06.1861 - 29.12.1866)":  list(range(1861, 1867))
    }
    for i in vorarlberg:
        for year in vorarlberg[i]:
            input_path = f"{path_vorarlberg}/{i}/{year}"
            if os.path.exists(input_path):
                dir_to_txt(input_path)

