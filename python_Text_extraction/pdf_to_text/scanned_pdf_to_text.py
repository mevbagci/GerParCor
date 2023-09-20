import multiprocessing
import argparse
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os
from tqdm import tqdm
from os import makedirs
import numpy as np
import cv2
import pathlib
from multiprocessing import Pool
from functools import partial
from typing import List

set_files = set()


def pdf_to_image(pdf_path: str, dpi: int, lang: str, output_path, bad_quali: bool = False) -> (int, str):
    """
    Function takes pdf scan as input and converts it to single images (one per page).
    Returns amount of pages
    :param pdf_path: path of the pdf-file
    :param dpi: Dpi number of the converted pictures from the pdf pages
    :param lang: Language of Tesseract OCR
    :param bad_quali: True if the scanned pdfs have a bad quality otherwise False
    :return:
    """
    output_path = pdf_path.replace("/pdf/", "/txt/")
    output_path = output_path.strip(".pdf") + "_image_safe"
    # output_path = output_path + "/" + pdf_path.split("/")[-1].strip(".pdf") + "_image_safe"
    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
    # Store all the pages of the PDF in a variable
    pages = convert_from_path(pdf_path, dpi)
    # Counter to store images of each page of PDF to image
    image_counter = 1
    # Iterate through all the pages stored above
    for page in pages:
        # Declaring filename for each page of PDF as JPG
        # For each page, filename will be:
        # PDF page 1 -> page_1.jpg
        # PDF page 2 -> page_2.jpg
        # PDF page 3 -> page_3.jpg
        # ....
        # PDF page n -> page_n.jpg
        filename = f"page_{image_counter}.jpg"
        # Save the image of the page in system
        page.save(f"{output_path}/{filename}", 'JPEG')
        if lang == "frk" or bad_quali:
            preprocess_bad_quality_text(f"{output_path}/{filename}")
        # Increment the counter to update filename
        image_counter += 1
    return image_counter, output_path


def preprocess_bad_quality_text(img_path: str):
    """
    :param img_path: path to image for rescale, convert the color from RGB to Gray, erode, dilate and remove/reduce the noises with a filter
    """
    # https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
    # https://nanonets.com/blog/ocr-with-tesseract/
    # base on: https://towardsdatascience.com/getting-started-with-tesseract-part-ii-f7f9a0899b3f & https://towardsdatascience.com/getting-started-with-tesseract-part-i-2a6a6b1cf75e
    img = cv2.imread(f"{img_path}", cv2.IMREAD_UNCHANGED)
    img_resize = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
    # img_gray = cv2.bitwise_not(img_gray)
    kernel = np.ones((2, 2), np.uint8)
    img_erode = cv2.erode(img_gray, kernel, iterations=1)
    img_dilate = cv2.dilate(img_erode, kernel, iterations=1)
    img_bilateral = cv2.bilateralFilter(img_dilate, 5, 75, 75)
    img_filter = cv2.threshold(img_dilate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # img_threshold = cv2.adaptiveThreshold(cv2.bilateralFilter(img_filter, 9, 75, 75), 255,
    #                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    cv2.imwrite(img_path, img_filter)


def image_to_text(image_path: str, pdf_path: str, file_limit: int, lang: str, out_dir: str) -> None:
    """
        Function converts images to text using OCR.
        :param pdf_path: path to the pdf-file
        :param file_limit:Number of converted Pages
        :param out_dir: output directory for the extraction
        :param image_path: path for the converted pages of the pdf-file
        :param lang: Language for Tesseract OCR extraction
    """
    # Variable to get count of total number of pages

    # Creating a text file to write the output

    # Open the file in append mode so that
    # All contents of all images are added to the same file
    # txt_data_name = str(os.path.basename(pdf_path)).replace(".pdf", ".txt")
    # txt_data_name = txt_data_name.replace(" ", "_")
    # txt_path = f"{out_dir}/{txt_data_name}"
    txt_path = pdf_path.replace("/pdf/", "/txt/").replace(".pdf", ".txt")
    makedirs(os.path.dirname(txt_path), exist_ok=True)
    with open(txt_path, "w", encoding="UTF-8") as f:
        # Iterate from 1 to total number of pages
        for i in range(1, file_limit):
            # Set filename to recognize text from
            # Again, these files will be:
            # page_1.jpg
            # page_2.jpg
            # ....
            # page_n.jpg
            filename = f"page_{i}.jpg"

            # Recognize the text as string in image using pytesserct
            text = str((pytesseract.image_to_string(Image.open(f"{image_path}/{filename}"), lang=lang)))

            # The recognized text is stored in variable text
            # Any string processing may be applied on text
            # Here, basic formatting has been done:
            # In many PDFs, at line ending, if a word can't
            # be written fully, a 'hyphen' is added.
            # The rest of the word is written in the next line
            # Eg: This is a sample text this word here GeeksF-
            # orGeeks is half on first line, remaining on next.
            # To remove this, we replace every '-\n' to ''.
            text = text.replace('-\n', '')

            # Finally, write the processed text to the file.
            f.write(text)

        # Close the file after writing all the text.

    # Delete saved images
    for i in range(1, file_limit):
        filename = f"page_{i}.jpg"
        os.remove(f"{image_path}/{filename}")
    if len(os.listdir(image_path)) == 0:
        # removing the file using the os.remove() method
        os.rmdir(image_path)
    else:
        # messaging saying folder not empty
        print("Folder is not empty")
    return


def get_all_path_pdf(path_dir: str):
    """
    :param path_dir: Directory of the pdf-files
    :return: set Path of the pdf-Files
    """
    for file in os.scandir(path_dir):
        if file.is_dir():
            get_all_path_pdf(file)
        elif (str(file.path)).endswith(".pdf"):
            set_files.add(str(file.path))
            if len(set_files) % 100 == 0:
                print(len(set_files))


def scanned_pdf_to_text(pdf_path: str, out_name_dir: str, bad_quali: bool, dpi=200, lang="eng"):
    """
         Base-on:                        https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/ +
                                        https://gitlab.texttechnologylab.org/Bagci/scannedpdftotext
         Overview possible languages:   https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html
        :param bad_quali: True if the scanned pdfs have a bad quality otherwise False
        :param out_name_dir: Directory for the output
        :param pdf_path: Directory of the pdf
        :param dpi: Dpi number of the converted pictures from the pdf pages
        :param lang: Language of Tesseract OCR
        :return: if the extraction was successfull
    """
    success = False
    try:
        counter, output_path = pdf_to_image(pdf_path, dpi, lang, out_name_dir, bad_quali)
        image_to_text(output_path, pdf_path, counter, lang, out_name_dir)
        success = True
    except Exception as e:
        print(e)
        success = False
    return success


def scan_dir_to_text(dir_path: str, out_name_dir: str, bad_quali: bool, dpi: int = 200, lang: str = "deu"):
    """
    Function to convert whole direcotry.
    :param out_name_dir: Directory for the output
    :param bad_quali: True if the scanned pdfs have a bad quality otherwise False
    :param dir_path: Directory of all pdf-files
    :param dpi: Dpi number of the converted pictures from the pdf pages
    :param lang: Language of Tesseract OCR
    """
    part_func = partial(scanned_pdf_to_text, dpi=dpi, lang=lang, out_name_dir=out_name_dir, bad_quali=bad_quali)
    number_core = int(int(multiprocessing.cpu_count() / 4) / 1)
    pool = Pool(number_core)
    # files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
    global set_files
    set_files = set()
    get_all_path_pdf(dir_path)
    files_exist = set()
    # print(set_files)
    for file_i in set_files:
        txt_file = file_i.replace("pdf", "txt")
        if os.path.exists(txt_file):
            files_exist.add(file_i)
    set_files = set_files.difference(files_exist)
    files = list(set_files)
    files.sort()
    result = list(tqdm(pool.imap_unordered(part_func, files),
                       desc=f"Converting files from: {dir_path.split('/')[-1]}", total=len(files)))
    pool.close()
    pool.join()
    successes, fails = 0, 0
    for i in result:
        if i:
            successes += 1
        else:
            fails += 1
    print(f"successes: {successes}, fails: {fails}")


def scan_List_to_text(dir_path: List[str], out_name_dir: str, bad_quali: bool, dpi: int = 200, lang: str = "deu"):
    """
    Function to convert whole direcotry.
    :param out_name_dir: Directory for the output
    :param bad_quali: True if the scanned pdfs have a bad quality otherwise False
    :param dir_path: Directory of all pdf-files
    :param dpi: Dpi number of the converted pictures from the pdf pages
    :param lang: Language of Tesseract OCR
    """
    part_func = partial(scanned_pdf_to_text, dpi=dpi, lang=lang, out_name_dir=out_name_dir, bad_quali=bad_quali)
    number_core = int(multiprocessing.cpu_count() / 4)
    pool = Pool(number_core)
    # files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
    # global set_files
    # set_files = set()
    # get_all_path_pdf(dir_path)
    # print(set_files)
    files = dir_path
    result = list(tqdm(pool.imap_unordered(part_func, files),
                       desc=f"Converting files from: {dir_path[0].split('/')[-1]}", total=len(files)))
    pool.close()
    pool.join()
    successes, fails = 0, 0
    for i in result:
        if i:
            successes += 1
        else:
            fails += 1
    print(f"successes: {successes}, fails: {fails}")


if __name__ == "__main__":
    quali = False
    dpi_convert = 300
    lang_old = "frk"
    lang_deu = "deu"
    # out_path = f"/storage/projects/abrami/GerParCor/txt/Austria/Bundesrat"
    out_base = f"/storage/projects/abrami/GerParCor/txt"
    base_path = f"/storage/projects/abrami/GerParCor/pdf"
    older_input = [
        "I", "II", "III", "IV", #frak
    ]


    # NiederOestereich
    niederaustria = [
        "IV. Gesetzgebungsperiode", "V. Gesetzgebungsperiode", "VI. Gesetzgebungsperiode", "VII. Gesetzgebungsperiode"
    ]
    path_nieder = f"{base_path}/Austria/Niederoestereich"
    out_nieder = f"{out_base}/Austria/Niederoestereich"

    # for i in niederaustria:
    #     input_path = f"{path_nieder}/{i}"
    #     scan_dir_to_text(input_path, out_nieder, True, dpi_convert, lang_deu)
    #
    # path_steiermark = f"{base_path}/Austria/Steiermark"
    # out_steiermark = f"{out_base}/Austria/Steiermark"
    # steiermark = [
    #     "1848", "1861 - 1866 (Periode I)", "1867 - 1869 (Periode II)", "1870 (Periode III)", "1871 - 1877 (Periode IV)", "1878 - 1883 (Periode V)", "1884 - 1889 (Periode VI)", "1890 - 1896 (Periode VII)", "1896 - 1902 (Periode VIII)", "1902 - 1908 (Periode IX)", "1909 - 1914 (Periode X)", "1918 - 1919", "1919 - 1920", "1920 - 1923 (Periode I)", "1923 - 1927 (Periode II)", "1927 - 1930 (Periode III)", "1931 - 1934 (Periode IV)", "1934 - 1938 (Periode V)"
    # ]
    #
    # for i in steiermark:
    #     input_path = f"{path_steiermark}/{i}"
    #     scan_dir_to_text(input_path, out_steiermark, True, dpi_convert, lang_old)


    list_failed = [
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1953-1954, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1955, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1956, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1957, Bd. 2.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1957-1958, Bd. 3.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1958-1959, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1959-1960, Bd. 5.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1960, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1961, Bd. 2.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1962-1963, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1963, Bd. 5.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1963-1964, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1964, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1965-1966, Bd. 3.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1966-1967, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1967, Bd. 5.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1967-1968, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1968-1969, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1969, Bd. 2.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1969-1970, Bd. 3.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1970, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1970-1971, Bd. 5.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1971, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1971-1972, Bd. 7.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1972-1973, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1973, Bd. 2.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1974-1975, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1975-1976, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1978-1979, Bd. 5.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1979, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1980, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1983, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1983-1984, Bd. 7.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1984, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1985, Bd. 2.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1986, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1986-1987, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1987, Bd. 7.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1988, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1989-1990, Bd. 3.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1990, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1990-1991, Bd. 5.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1991, Bd. 6.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1991-1992, Bd. 7.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1992, Bd. 1.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1992-1993, Bd. 2.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1993, Bd. 3.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1993-1994, Bd. 4.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1994, Bd. 5.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1995, Bd. 7.pdf",
        # "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)/1995-1996, Bd. 8.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag W\u00fcrttemberg/ Erste Kammer (1820-1847, 1848-1918)/1836, Bd. 1.pdf"
    ]
    scan_List_to_text(list_failed, f"/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/older/Landtag Baden-W\u00fcrttemberg (1953-1996)", True, dpi_convert, lang_old)
    list_repaired = [
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/0/00_0005_10051952.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/0/00_0008_28051952.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/1/01_0016_28011954.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/2/02_0084_15071959.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/2/02_0085_14101959.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/2/02_0086_11111959.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/2/02_0090_09121959.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0012_27101960.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0058_14061962.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0073_06121962.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0081_28031963.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0087_20061963.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0089_11071963.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0112_27021964.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0113_05031964.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/3/03_0115_19031964.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/4/04_0095_11051967.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/4/04_0099_20071967.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/4/04_0105_09111967.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/4/04_0106_23111967.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/4/04_0112_07121967.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/4/04_0124_28031968.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/4/04_0125_29031968.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/5/05_0019_29011969.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/5/05_0075_08071970.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/5/05_0108_24061971.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/5/05_0109_08071971.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/5/05_0135_02031972.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0030_28061973.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0032_10071973.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0041_12121973.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0050_01031974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0054_09051974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0056_20061974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0057_21061974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0059_26061974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0060_27061974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0068_14111974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0069_28111974.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0073_23011975.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0093_25091975.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0100_03121975.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/6/06_0107_18021976.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/7/07_0062_19101978.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/7/07_0063_29111978.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/7/07_0066_07121978.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/7/07_0083_27091979.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/7/07_0087_29111979.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/7/07_0092_30011980.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/7/07_0093_31011980.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/8/08_0008_16071980.pdf",
        "/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg/8/08_0077_10111983.pdf",
    ]
    scan_List_to_text(list_repaired,
                      f"/storage/projects/abrami/GerParCor/pdf/Germany/BadenWuertemmberg",
                      True, dpi_convert, lang_deu)

    # older_input = [
    #     # "Alter Landtag Württemberg (1797-1799)",
    #     # "Landtag Baden-Württemberg (1953-1996)",
    #     "Landtag Württemberg/ Zweite Kammer (1820-1847, 1848-1918, 1920-1933)",
    #     # "Landtag Württemberg/ Erste Kammer (1820-1847, 1848-1918)",
    #     # "Landtag Württemberg-Baden (1946-1952)",
    #     # "Landtag Württemberg-Hohenzollern (1946-1952)",
    #     # "Ständeversammlung Württemberg (1815-1819)",
    #     # "Verfassungsgebende Landesversammlung Baden-Württemberg",
    #     # "Verfassungsgebende Landesversammlungen Württemberg (1849-1850, 1919-1920)",
    #     # "Verfassungsgebende Landesversammlung Württemberg-Baden",
    #     # "Verfassungsgebende Landesversammlung Württemberg-Hohenzollern"
    #
    # ]
    # for i in older_input:
    #     input_path = f"/storage/projects/abrami/GerParCor/pdf/Austria/Bundesrat/{i}"
    #     scan_dir_to_text(input_path, out_path, True, dpi_convert, lang_old)
    # with open("/storage/xmi/GerParCorDownload/emptySofa.txt", "r", encoding="UTF-8") as txt:
    #     all_files = txt.readlines()
    #     files = []
    #     for file_i in all_files:
    #         new_name = file_i.replace("xmi.gz", "pdf").replace("/xmi/", "/pdf/").replace("\n", "").replace("file:", "")
    #         new_file = new_name.split("/")[-1]
    #         index_i = new_file.find("_")
    #         new_file = new_file.replace("_", " ")
    #         new_file = new_file[:index_i] + "_" + new_file[index_i+1:]
    #         new_name = new_name.split("/")
    #         new_name = new_name[:-1] + [new_file]
    #         new_name = "/".join(new_name)
    #         files.append(new_name)
    #     scan_List_to_text(files, out_path, quali, dpi_convert, "deu")
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-p", "--path_directory", help="path to the directory with the .pdf files")
    # parser.add_argument("-o", "--out", default="pdf_to_txt_out",
    #                     help="directory path for the outputs of the Tessseract OCR extraction")
    # parser.add_argument("-q", "--quali", default=False,
    #                     help="Boolean True if scanned pdf documents have a bad quality otherwise False")
    # parser.add_argument("-d", "--dpi", default=200, help="The dpi for converting ever page to a picture")
    # parser.add_argument("-l", "--lang", default="deu", help="The language for the Tesseract OCR extraction")
    # args = parser.parse_args()
    # scan_dir_to_text(dir_path=args.path_directory, out_name_dir=args.out, bad_quali=args.quali, dpi=args.dpi,
    #                  lang=args.lang)
