import os
import time

import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import urllib
import pandas as pd
from urllib import request
from urllib.parse import quote
import json
from tqdm import tqdm

def bs4_downloader(html_dir):
    with open(html_dir, "r") as f:
        html_input = f.read()
        soup = BeautifulSoup(html_input, 'html.parser')
        soup.findAll('table')[0].findAll('tr')
        print("h")


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
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Austria/Vorarlberg'
    prefs = {'download.default_directory': dir_download, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    # chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(page)
    time.sleep(5)
    try:
        # accept cookies
        driver.find_element(By.XPATH, f'//*[@id="CybotCookiebotDialogBodyButtonDecline"]').click()
    except Exception as ex:
        print(ex)
    driver.execute_script(
        f'document.querySelector("body > form > table:nth-child(14) > tbody > tr:nth-child(3) > td:nth-child(1) > table > tbody > tr:nth-child(1) > td > select > option:nth-child(1)")')
    driver.execute_script(f'document.querySelector("#fdPeriodTX > option:nth-child(1)")')
    driver.find_element(By.XPATH, f'/html/body/form/table[4]/tbody/tr[3]/td[1]/table/tbody/tr[3]')
    driver.find_element(By.XPATH,
                        f'/html/body/form/table[4]/tbody/tr[3]/td[1]/table/tbody/tr[3]/td/select[1]/option[1]').click()
    driver.find_element(By.XPATH, f'/html/body/form/table[4]/tbody/tr[1]/td/table[1]/tbody/tr/td[2]/button[1]').click()


if __name__ == '__main__':
    test = f"https://suche.vorarlberg.at/VLR/vlr_gov.nsf/0/10BB6954AA682D1CC12587EB003D5A83?OpenDocument"
    # bs4_downloader(test)
    # page_name = f"https://vorarlberg.at/web/landtag/lis"
    # download_protokoll(test)
    downlaod_from_tsv(f"vorarlberg.tsv")