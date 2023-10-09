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
import gzip

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
        link_i = driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[1]/table/tbody/tr/td[1]/a').get_attribute("href")
        text_i = driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[1]/table/tbody/tr/td[2]/b/font').text
        all_links[text_i]={
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
                link_inter = driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[1]/a').get_attribute("href")
                link_inter_text = driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[2]/b/font').text
                number_inter = int(driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[3]/font').text)
                if link_inter is not None:
                    all_inter_links.append(link_inter)
                    all_links[link_id]["inter"][link_inter_text] = {
                        "link": link_inter,
                        "number": number_inter,
                        "protocol": {}
                    }
                else:
                    link_inter = driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[1]/a[2]').get_attribute("href")
                    link_inter_text = driver.find_element(By.XPATH,
                                                          f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[2]/table/tbody/tr/td[2]/b[2]/font').text
                    number_inter = int(driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[3]/font').text)
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
                    link_element = driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[5]/font/a')
                    link_protocol = link_element.get_attribute("href")
                    typ_protocol = driver.find_element(By.XPATH, f'/html/body/form/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[{counter}]/td[4]').text
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
    download_protokoll(page_search)
    # downlaod_from_tsv(f"vorarlberg.tsv")