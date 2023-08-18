import gzip
import json
import os
import time
from bs4 import *
from selenium import webdriver
import pandas as pd
import glob
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
from tqdm import tqdm
import warnings
import glob


def download_landtag_evidenz(page, name_dokumente):
    # page = f"https://portal.tirol.gv.at/LteWeb/public/sitzung/sitzungsbericht/sitzungsberichtList.xhtml?cid=1"
    chrome_options = webdriver.ChromeOptions()
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Austria/Tirol/{name_dokumente}'
    prefs = {'download.default_directory': dir_download, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(page)
    time.sleep(5)
    # driver.find_element(By.XPATH, f'//*[@id="listContent:j_id_4v_9"]').click()
    # time.sleep(1)
    counter_menu = 1
    y = True
    while y:
        try:
            driver.find_element(By.XPATH, '//*[@id="listContent:j_id_4i:menu"]').click()
            driver.find_element(By.XPATH, f'//*[@id="listContent:j_id_4i:menu_{counter_menu}"]').click()
            driver.find_element(By.XPATH, f'//*[@id="listContent:j_id_4v_9"]').click()
            time.sleep(0.5)
            text_periode = driver.find_element(By.XPATH, '//*[@id="listContent:j_id_4i:menu"]').text
            os.makedirs(f"{dir_download}/{text_periode}", exist_ok=True)
            x = True
            counter = 0
            while x:
                try:
                    for i in range(0, 25):
                        driver.find_element(By.XPATH,
                                            f'//*[@id="listContent:resultForm:resultTable:{counter}:j_id_52"]').click()
                        text_sitzung = driver.find_element(By.XPATH,
                                                           f'//*[@id="listContent:resultForm:resultTable_data"]/tr[{i + 1}]/td[2]').text
                        text_bezeichung = driver.find_element(By.XPATH,
                                                              f'//*[@id="listContent:resultForm:resultTable:{counter}:fileTypeIcon"]/span[2]').text
                        text_in = text_bezeichung.replace(" ", "_")
                        if "ä" in text_in:
                            text_in = text_in.replace("ä", "_C3_A4")
                        if "/" in text_in:
                            text_in = text_in.replace(f"/", "_2F")
                        while not os.path.exists(f"{dir_download}/{text_in}.pdf") and not os.path.exists(
                                f"{dir_download}/{text_in}.docx"):
                            time.sleep(0.5)
                        text_bezeichung = text_bezeichung.replace("/", ";")
                        text_sitzung = text_sitzung.replace("/", ";")
                        end = "pdf"
                        if os.path.exists(f"{dir_download}/{text_in}.docx"):
                            end = "docx"
                        os.rename(f"{dir_download}/{text_in}.{end}",
                                  f"{dir_download}/{text_periode}/{text_bezeichung}_{text_sitzung}.{end}")
                        counter += 1
                    driver.find_element(By.XPATH,
                                        f'//*[@id="listContent:resultForm:resultTable_paginator_top"]/a[3]').click()
                    print(f"Downloaded Tirol {counter}")
                    time.sleep(3)
                except Exception as ex:
                    # print(ex)
                    x = False
            counter_menu += 1
            print(counter_menu)
        except Exception as ex:
            print(ex)
            y = False


if __name__ == '__main__':
    document_name = f"Sitzungsbericht"
    page_name = f"https://portal.tirol.gv.at/LteWeb/public/sitzung/{document_name.lower()}/{document_name.lower()}List.xhtml"
    download_landtag_evidenz(page_name, document_name)
