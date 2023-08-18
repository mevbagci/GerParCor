import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import urllib
import pandas as pd
from urllib import request
from urllib.parse import quote

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
    download_dir = f"/home/staff_homes/bagci/data/temp"
    df = pd.read_csv(tsv_dir, sep="\t", encoding="utf-8", header=None)
    for index, row in df.iterrows():
        name = row[0]
        if name is None or name == "":
            continue
        year = int(row[1])
        link = row[2]
        link_new = link.split("?OpenDocument")[0]
        url_enconde_name = quote(name, safe="")
        link_new = f"{link_new}/$FILE/{url_enconde_name}.pdf"
        file_dir = f"{download_dir}/{year}/{name}.pdf"

        download_pdf(file_dir, link_new)
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
    downlaod_from_tsv(f"~/data/temp/vorarlberg.tsv")