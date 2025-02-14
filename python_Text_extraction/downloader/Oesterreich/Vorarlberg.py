import copy
import os
import time

import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import urllib
import pandas as pd
from urllib import request
from urllib.parse import quote
import json
from tqdm import tqdm
import gzip
import locale
from datetime import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from help_function import reset_set_files, get_set_files, get_all_path_files


def bs4_downloader(html_dir):
    with open(html_dir, "r") as f:
        html_input = f.read()
        soup = BeautifulSoup(html_input, 'html.parser')
        soup.findAll('table')[0].findAll('tr')
        print("h")


def get_last_downloaded_file(directory):
    return os.listdir(directory)


def download_pdf(file_name, url):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    response = urllib.request.urlopen(url)
    file = open(file_name, 'wb')
    file.write(response.read())
    file.close()


def downlaod_from_tsv(tsv_dir):
    download_dir = f"/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg"
    df = pd.read_csv(tsv_dir, sep="\t", encoding="utf-8", header=None)
    failed = []
    counter_number = 0
    for index, row in tqdm(df.iterrows()):
        name = row[0]
        if name is None or name == "" or name is np.nan:
            continue
        year = int(row[1])
        link = row[2]
        link_new = link.split("?OpenDocument")[0]
        url_enconde_name = quote(name, safe="")
        link_new = f"{link_new}/$FILE/{url_enconde_name}.pdf"
        other_link = row[3]
        counter = 1
        file_dir = f"{download_dir}/{year}/{name}#1.pdf"
        while os.path.exists(file_dir):
            counter += 1
            file_dir = f"{download_dir}/{year}/{name}#{counter}.pdf"
        try:
            download_pdf(file_dir, link_new)
            counter_number += 1
        except Exception as ex:
            try:
                download_pdf(file_dir, other_link)
                counter_number += 1
            except Exception as ex1:
                try:
                    file_name_i = quote(other_link.split("/")[-1].split(".pdf")[0], safe="")
                    start_url = other_link.replace(other_link.split("/")[-1], "")
                    alternative_link = f"{start_url}{file_name_i}.pdf"
                    download_pdf(file_dir, alternative_link)
                    counter_number += 1
                except Exception as ex:
                    failed.append(f"{year}-{name}")
                    print(ex)
    print(counter_number)
    os.makedirs(os.path.dirname(f"/storage/projects/bagci/test"), exist_ok=True)
    with open(f"/storage/projects/bagci/test/failed.json", "w", encoding="UTF-8") as json_file:
        json.dump(failed, json_file, indent=2)
    print("h")


def download_protokoll(page):
    chrome_options = webdriver.ChromeOptions()
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg_test'
    prefs = {'download.default_directory': dir_download, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(page)
    time.sleep(5)
    all_links = {}
    for i in list(range(2, 35)):
        link_i = driver.find_element(By.XPATH,
                                     f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[1]/table/tbody/tr/td[1]/a').get_attribute(
            "href")
        text_i = driver.find_element(By.XPATH,
                                     f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[1]/table/tbody/tr/td[2]/b/font').text
        all_links[text_i] = {
            "link": link_i,
            "inter": {}
        }
        # all_links.append(link_i)
    all_inter_links = []
    for link_id in tqdm(all_links):
        link_i = all_links[link_id]["link"]
        driver.get(link_i)
        time.sleep(2)
        counter = 3
        while True:
            try:
                link_inter = driver.find_element(By.XPATH,
                                                 f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[1]/a').get_attribute(
                    "href")
                link_inter_text = driver.find_element(By.XPATH,
                                                      f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[2]/b/font').text
                number_inter = int(driver.find_element(By.XPATH,
                                                       f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[3]/font').text)
                if link_inter is not None:
                    all_inter_links.append(link_inter)
                    all_links[link_id]["inter"][link_inter_text] = {
                        "link": link_inter,
                        "number": number_inter,
                        "protocol": {}
                    }
                else:
                    link_inter = driver.find_element(By.XPATH,
                                                     f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[1]/a[2]').get_attribute(
                        "href")
                    link_inter_text = driver.find_element(By.XPATH,
                                                          f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[2]/b[2]/font').text
                    number_inter = int(driver.find_element(By.XPATH,
                                                           f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[3]/font').text)
                    if link_inter is not None:
                        all_inter_links.append(link_inter)
                        all_links[link_id]["inter"][link_inter_text] = {
                            "link": link_inter,
                            "number": number_inter,
                            "protocol": {}
                        }
            except:
                if counter > 50:
                    break
            counter += 1
        # print("h")
    for link_id in all_links:
        for inter_link_id in tqdm(all_links[link_id]["inter"], desc=f"Save all Urls of {link_id}"):
            inter_link = all_links[link_id]["inter"][inter_link_id]["link"]
            number_inter = all_links[link_id]["inter"][inter_link_id]["number"]
            counter = 0
            driver.get(inter_link)
            start_loader = False
            time.sleep(2)
            while True:
                try:
                    link_element = driver.find_element(By.XPATH,
                                                       f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[5]/font/a')
                    link_protocol = link_element.get_attribute("href")
                    typ_protocol = driver.find_element(By.XPATH,
                                                       f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[4]').text
                    if link_protocol is not None:
                        all_links[link_id]["inter"][inter_link_id]["protocol"][link_element.text] = {
                            "link": link_protocol,
                            "typ": typ_protocol
                        }
                    start_loader = True
                except:
                    if start_loader:
                        break
                counter += 1
            # for protokoll_id in all_links[link_id]["inter"][inter_link_id]["protocol"]:
            #     protokoll = all_links[link_id]["inter"][inter_link_id]["protocol"][protokoll_id]
            #     driver.get(protokoll)
            #     link_pdf = driver.find_element(By.XPATH, f'/html/body/form/a[5]').get_attribute("href").replace('javascript:OpenPDF("', "").replace('")', "")
            #     file_name = f"{dir_download}/{link_id}/{inter_link_id}/{protokoll_id}.pdf"
            #     file_name = f"{dir_download}/{link_id}/{inter_link_id}/{protokoll_id}.pdf"
            #     print("h")
    save_json(all_links, f"/storage/projects/abrami/GerParCor/links/austria/Vorarlberg/vorarlberg.json")


def download_saved_links(type_download=f"Protokoll"):
    chrome_options = webdriver.ChromeOptions()
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg_temp3'
    download_directory = f'/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg_test4'
    prefs = {'download.default_directory': dir_download, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    if not os.path.exists(f"/storage/projects/abrami/GerParCor/links/austria/Vorarlberg/vorarlberg.json"):
        download_protokoll(f"https://suche.vorarlberg.at/VLR/vlr_gov.nsf/nachLandtagsperiode?OpenForm")
    all_links = read_json(f"/storage/projects/abrami/GerParCor/links/austria/Vorarlberg/vorarlberg.json")
    downloads = []
    failed = []
    start = True
    for link_id in all_links:
        for inter_id in all_links[link_id]["inter"]:
            for c, protocol_id in enumerate(
                    tqdm(all_links[link_id]["inter"][inter_id]["protocol"], desc=f"{link_id} ; {inter_id}")):
                if link_id == "28. Landtag (Oktober 2004 - September 2009)" and inter_id == "2007-09" and c == 2:
                    start = True
                if start:
                    complete_data = False
                    special_key = f"{link_id}#__#{inter_id}#__#{protocol_id}"
                    type_i = all_links[link_id]["inter"][inter_id]["protocol"][protocol_id]["typ"]
                    link_i = all_links[link_id]["inter"][inter_id]["protocol"][protocol_id]["link"]
                    split_inter_id = inter_id.split("-")
                    for protocol_id2 in all_links[link_id]["inter"][inter_id]["protocol"]:
                        if type_i == type_download:
                            if "komplette" in protocol_id2:
                                complete_data = True
                    if len(split_inter_id) <= 2:
                        year_sitzung = split_inter_id[0]
                    else:
                        year_sitzung = split_inter_id[1]
                    sitzung = str(split_inter_id[-1])
                    if sitzung.split(" ")[0].isalpha():
                        sitzung = split_inter_id[1]
                        year_sitzung = split_inter_id[0]
                    if type_i == type_download:
                        # start_id = int(link_id.split(".")[0])
                        # if start_id > 27:
                        #     continue
                        if complete_data:
                            if "komplette" not in protocol_id:
                                continue
                        downloads.append(f"{special_key}##link##{link_i}")
                        driver.get(link_i)
                        counter = 0
                        # wait = WebDriverWait(driver, 10)
                        # wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/form/a[5]')))
                        # link_download = driver.find_element(By.XPATH, f'/html/body/form/a[5]').get_attribute("href").replace('javascript:OpenPDF("', "").replace('")', "")
                        # download_pdf(f"{dir_download}/{link_id}/{inter_id.split('-')[0]}/{protocol_id.split('„')[0]}.pdf", link_download)
                        while True:
                            files = get_last_downloaded_file(dir_download)
                            if len(files) > 0:
                                if files[-1].endswith(".pdf"):
                                    time.sleep(1)
                                    infos_i = driver.find_element(By.XPATH,
                                                                  f'/html/body/form/table/tbody/tr/td[2]').text.split(
                                        "\n")
                                    date_i = "XXXX"
                                    for info_i in infos_i:
                                        if "Behandelt im Landtag " in info_i:
                                            date_i = info_i.split("Behandelt im Landtag ")[-1].split(" ")[0]
                                            if "./" in date_i:
                                                date_i = date_i.replace("./", "-")
                                            if "/" in date_i:
                                                date_i = date_i.split("/")
                                                date_i = f"{date_i[1]}.{date_i[0]}.{date_i[2]}"
                                            break
                                    if date_i == "XXXX" and "am " in protocol_id:
                                        date_i = protocol_id.split("am ")[-1]
                                        if ". " in date_i:
                                            date_i = date_i.split(" ")
                                            date_i = f"{date_i[0]} {date_i[1]} {date_i[2]}"
                                            try:
                                                locale.setlocale(locale.LC_ALL, 'de_AT.utf8')
                                                date_test = datetime.strptime(date_i, "%d. %B %Y")
                                                date_i = date_test.strftime("%d.%m.%Y")
                                                # date_i = f"{date_test.day}.{date_test.month}.{date_test.year}"
                                            except:
                                                pass
                                        else:
                                            date_i = date_i.split(" ")[0]
                                        if "./" in date_i:
                                            date_i = date_i.replace("./", "-")
                                        if "/" in date_i:
                                            date_i = date_i.split("/")
                                            date_i = f"{date_i[1]}.{date_i[0]}.{date_i[2]}"
                                    if date_i == "XXXX":
                                        list_files = get_last_downloaded_file(dir_download)
                                        for i in list_files:
                                            try:
                                                os.remove(f"{dir_download}/{i}")
                                            except:
                                                pass
                                        break
                                    out_name = f"{download_directory}/{link_id}/{year_sitzung}/{sitzung}##{date_i}##{files[-1]}"
                                    os.makedirs(f"{download_directory}/{link_id}/{year_sitzung}", exist_ok=True)
                                    os.rename(f"{dir_download}/{files[-1]}", out_name)
                                    time.sleep(1)
                                    break
                                else:
                                    time.sleep(0.1)
                            else:
                                time.sleep(0.01)
                            counter += 1
                            if counter > 5000:
                                failed.append(special_key)
                                list_files = get_last_downloaded_file(dir_download)
                                for i in list_files:
                                    try:
                                        os.remove(f"{dir_download}/{i}")
                                    except:
                                        pass
                                break
    save_json(failed, "/storage/projects/abrami/GerParCor/links/austria/Vorarlberg/failed.json")
    # part_func = partial(get_download_page)
    # number_core = int(multiprocessing.cpu_count()-1)
    # pool = Pool(number_core)
    # result = list(tqdm(pool.imap_unordered(part_func, downloads),
    #                    desc=f"Downloadung", total=len(downloads)))
    # pool.close()
    # pool.join()
    # successes, fails = 0, 0
    # for i in result:
    #     if i:
    #         successes += 1
    #     else:
    #         fails += 1
    # print(f"successes: {successes}, fails: {fails}")


def get_download_page(special_url):
    chrome_options = webdriver.ChromeOptions()
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg_test2'
    prefs = {'download.default_directory': dir_download, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    link_i = special_url.split("##link##")[-1]
    driver.get(link_i)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/form/a[5]')))
    link_download = driver.find_element(By.XPATH, f'/html/body/form/a[5]').get_attribute("href").replace(
        'javascript:OpenPDF("', "").replace('")', "")
    link_names = special_url.split("##link##")[0].split("#__#")
    try:
        download_pdf(f"{dir_download}/{link_names[0]}/{link_names[1].split('-')[0]}/{link_names[2].split('„')[0]}.pdf",
                     link_download)
        while True:
            if os.path.exists(
                    f"{dir_download}/{link_names[0]}/{link_names[1].split('-')[0]}/{link_names[2].split('„')[0]}.pdf"):
                break
            else:
                time.sleep(0.5)
        return True
    except:
        return False
    # print("h")


def merge_all_pdfs(pdf_dir):
    reset_set_files()
    get_all_path_files(pdf_dir, ".pdf")
    all_files = list(get_set_files())
    all_files = sorted(all_files)
    files_divded = {}
    for file_i in tqdm(all_files, desc=f"Divid files"):
        splitet_file = file_i.split("##")
        key_i = f"{splitet_file[0]}"
        if key_i not in files_divded:
            files_divded[key_i] = []
        files_divded[key_i].append(file_i)
    copy_files = copy.deepcopy(files_divded)
    for key_i in copy_files:
        if len(copy_files[key_i]) == 1:
            del files_divded[key_i]
    for key_i in tqdm(files_divded, desc=f"Merge files"):
        mergedObject = PdfMerger()
        files_sorted = sorted(copy.deepcopy(files_divded[key_i]), key=os.path.getmtime)
        for file_i in files_sorted:
            mergedObject.append(PdfReader(file_i, strict=False))
        year_x = files_sorted[0].split("##")[1]
        mergedObject.write(f"{key_i}##{year_x}##Komplette_Sitzung.pdf")
        for file_i in files_sorted:
            out_i = key_i.replace("Vorarlberg_test4", "Vorarlberg_merged4")
            file_split = file_i.split("/")[-1]
            os.makedirs(f"{out_i}", exist_ok=True)
            os.rename(file_i, f"{out_i}/{file_split}")
            time.sleep(0.5)


def remerge_all_pdfs(pdf_dir):
    reset_set_files()
    get_all_path_files(pdf_dir, ".pdf")
    all_files = list(get_set_files())
    all_files = sorted(all_files)
    files_divded = {}
    for file_i in tqdm(all_files, desc=f"Divid files"):
        splitet_file = file_i.split("/")
        splits = splitet_file[:-2] + splitet_file[-1:]
        splitet_file = "/".join(splits).split("##")
        key_i = f"{splitet_file[0]}##{splitet_file[1]}"
        if key_i not in files_divded:
            files_divded[key_i] = []
        files_divded[key_i].append(file_i)
    copy_files = copy.deepcopy(files_divded)
    for key_i in copy_files:
        if len(copy_files[key_i]) == 1:
            del files_divded[key_i]
    for key_i in tqdm(files_divded, desc=f"Merge files"):
        mergedObject = PdfMerger()
        files_sorted = sorted(copy.deepcopy(files_divded[key_i]), key=os.path.getmtime)
        # print("h")
        out_i = key_i.replace("Vorarlberg_merged3", "Vorarlberg_test3")
        for file_i in files_sorted:
            mergedObject.append(PdfReader(file_i, strict=False))
        mergedObject.write(f"{out_i}##Komplette_Sitzung.pdf")

        # for file_i in files_divded[key_i]:
        #     out_i = key_i.replace("Vorarlberg_merged3", "Vorarlberg_test3")
        #     file_split = file_i.split("/")[-1]
        #     os.makedirs(f"{out_i}", exist_ok=True)
        #     os.rename(file_i, f"{out_i}/{file_split}")
        #     time.sleep(0.5)


def delete_ocr_typed_files(pdf_dir):
    reset_set_files()
    get_all_path_files(pdf_dir, ".pdf")
    all_files = list(get_set_files())
    all_files = sorted(all_files)
    for file_i in tqdm(all_files, desc=f"Divid files"):
        splitet_file = file_i.split("/")
        new_place = file_i.replace("Vorarlberg_test4", "Vorarlberg_test4_with_ocr")
        if os.path.exists(new_place):
            continue
        if splitet_file[-2].isnumeric():
            if int(splitet_file[-2]) > 1938:
                break
        pdf_file = PdfReader(file_i, strict=False)
        pdf_newfile = PdfWriter()
        for page in range(0, int(len(pdf_file.pages) / 2)):
            pdf_newfile.add_page(pdf_file.pages[page])
        os.makedirs(os.path.dirname(new_place), exist_ok=True)
        os.rename(file_i, new_place)
        time.sleep(0.1)
        pdf_newfile.write(f"{file_i}")
        # print("h")


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


if __name__ == '__main__':
    test = f"https://suche.vorarlberg.at/VLR/vlr_gov.nsf/0/10BB6954AA682D1CC12587EB003D5A83?OpenDocument"
    # bs4_downloader(test)
    page_name = f"https://vorarlberg.at/web/landtag/lis"
    page_search = f"https://suche.vorarlberg.at/VLR/vlr_gov.nsf/nachLandtagsperiode?OpenForm"
    # download_protokoll(page_search)
    # downlaod_from_tsv(f"vorarlberg.tsv")
    # download_saved_links()
    merge_all_pdfs(f"/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg_test4")
    # remerge_all_pdfs(f"/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg_merged3")
    # delete_ocr_typed_files(f"/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg_test4")
