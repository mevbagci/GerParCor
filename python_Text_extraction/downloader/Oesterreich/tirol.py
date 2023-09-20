import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_last_downloaded_file(directory):
    return os.listdir(directory)


def download_landtag_evidenz(page, name_document):
    # page = f"https://portal.tirol.gv.at/LteWeb/public/sitzung/sitzungsbericht/sitzungsberichtList.xhtml?cid=1"
    chrome_options = webdriver.ChromeOptions()
    # dir_download = f'/storage/projects/bagci/test/Tirol/{name_document}'
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Austria/Tirol/{name_document}'
    download_temp = f'/storage/projects/bagci/test/temp'
    prefs = {'download.default_directory': download_temp, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(page)
    time.sleep(5)
    # driver.find_element(By.XPATH, f'//*[@id="listContent:j_id_4v_9"]').click()
    driver.find_element(By.XPATH, f'//*[@id="listContent:j_id_4v_9"]').click()
    time.sleep(1)
    counter_menu = driver.find_element(By.XPATH, f'//*[@id="listContent:resultForm:resultTable_paginator_top"]/span[1]').text
    counter_end = int(counter_menu.split("von ")[-1])
    counter_menu = int(int(counter_menu.split("von ")[-1])/25)+1
    counter_i = 0
    for page_site in list(range(1, counter_menu+1)):
        for id_i in list(range(0,25)):
            if counter_i >= counter_end:
                break
            element = driver.find_element(By.XPATH, f'//*[@id="listContent:resultForm:resultTable:{counter_i}:j_id_52"]')
            sitzung = driver.find_element(By.XPATH, f'//*[@id="listContent:resultForm:resultTable_data"]/tr[{id_i+1}]/td[2]')
            element_name = element.text
            sitzung_name = sitzung.text
            # periode = sitzung_name.split(" Periode")[0].split(" ")[-1]
            try:
                periode = re.findall(r'\d{4}', element_name)[0]
            except:
                try:
                    periode = re.findall(r'\d{4}', sitzung_name)[0]
                except:
                    periode = "not assignable"
            file_name = f"{sitzung_name}_{element_name}.pdf".replace("/", "_")
            if os.path.exists(f"{dir_download}/{periode} Periode/{file_name}"):
                counter_i += 1
                continue
            element.click()
            while len(get_last_downloaded_file(download_temp))==0:
                time.sleep(0.5)
            while get_last_downloaded_file(download_temp)[0].endswith(".crdownload"):
                time.sleep(0.5)
            time.sleep(1)
            downloaded_elements = get_last_downloaded_file(download_temp)
            os.makedirs(f"{dir_download}/{periode} Periode", exist_ok=True)
            os.rename(f"{download_temp}/{downloaded_elements[0]}", f"{dir_download}/{periode} Periode/{file_name}")
            time.sleep(1)
            for i in get_last_downloaded_file(download_temp):
                os.remove(f"{download_temp}/{i}")
            counter_i += 1
        driver.find_element(By.XPATH, f'//*[@id="listContent:resultForm:resultTable_paginator_top"]/a[3]').click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="listContent:resultForm:resultTable:{counter_i}:j_id_52"]')))
        print(counter_i)
        # time.sleep(2)
    # while y:
    #     try:
    #         driver.find_element(By.XPATH, '//*[@id="listContent:j_id_4i:menu"]').click()
    #         driver.find_element(By.XPATH, f'//*[@id="listContent:j_id_4i:menu_{counter_menu}"]').click()
    #         driver.find_element(By.XPATH, f'//*[@id="listContent:j_id_4v_9"]').click()
    #         time.sleep(0.5)
    #         text_periode = driver.find_element(By.XPATH, '//*[@id="listContent:j_id_4i:menu"]').text
    #         os.makedirs(f"{dir_download}/{text_periode}", exist_ok=True)
    #         x = True
    #         counter = 0
    #         while x:
    #             try:
    #                 range_max = driver.find_element(By.XPATH, f'//*[@id="listContent:resultForm:resultTable"]/div[1]/div/span').text.split("-")[-1].split(" ")[0]
    #                 for i in range(0, int(range_max)):
    #                     time.sleep(0.5)
    #                     text_sitzung = driver.find_element(By.XPATH,
    #                                                        f'//*[@id="listContent:resultForm:resultTable_data"]/tr[{i + 1}]/td[2]').text
    #                     text_bezeichung = driver.find_element(By.XPATH,
    #                                                           f'//*[@id="listContent:resultForm:resultTable:{counter}:fileTypeIcon"]/span[2]').text
    #                     # if os.path.exists(
    #                     #         f"{dir_download}/{text_periode}/{text_bezeichung}_{text_sitzung}.pdf") or os.path.exists(
    #                     #         f"{dir_download}/{text_periode}/{text_bezeichung}_{text_sitzung}.docx"):
    #                     #     counter += 1
    #                     #     continue
    #                     driver.find_element(By.XPATH,
    #                                         f'//*[@id="listContent:resultForm:resultTable:{counter}:j_id_52"]').click()
    #                     while len(get_last_downloaded_file(download_temp))==0:
    #                         time.sleep(0.5)
    #                     while True:
    #                         last_element = get_last_downloaded_file(download_temp)[0]
    #                         if last_element.endswith(".pdf") or last_element.endswith(".docx") or last_element.endswith(".doc"):
    #                             break
    #                         time.sleep(0.5)
    #                     text_in = last_element.split("/")[-1]
    #                     end = text_in.split(".")[-1]
    #                     text_bezeichung = text_bezeichung.replace("/", ";")
    #                     text_sitzung = text_sitzung.replace("/", ";")
    #                     os.rename(f"{download_temp}/{last_element}",
    #                               f"{dir_download}/{text_periode}/{text_bezeichung}_{text_sitzung}.{end}")
    #                     counter += 1
    #                 driver.find_element(By.XPATH,
    #                                     f'//*[@id="listContent:resultForm:resultTable_paginator_top"]/a[3]').click()
    #                 print(f"Downloaded Tirol {name_document} {counter}")
    #                 loading = True
    #                 while loading:
    #                     try:
    #                         driver.find_element(By.XPATH, f'//*[@id="listContent:resultForm:resultTable:0:j_id_52"]')
    #                         time.sleep(1)
    #                     except:
    #                         loading = False
    #                 time.sleep(3)
    #             except Exception as ex:
    #                 # print(ex)
    #                 x = False
    #         counter_menu += 1
    #         print(counter_menu)
    #     except Exception as ex:
    #         print(ex)
    #         y = False


if __name__ == '__main__':
    document_names = ["Kurzprotokoll", "Sitzungsbericht"]
    for document_name in document_names:
        page_name = f"https://portal.tirol.gv.at/LteWeb/public/sitzung/{document_name.lower()}/{document_name.lower()}List.xhtml"
        download_landtag_evidenz(page_name, document_name)
