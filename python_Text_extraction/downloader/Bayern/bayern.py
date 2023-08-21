import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import urllib.request
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from tqdm import tqdm


def dowload_pdf(file_name, url):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    response = urllib.request.urlopen(url)
    file = open(file_name, 'wb')
    file.write(response.read())
    file.close()


def downloader():
    chrome_options = webdriver.ChromeOptions()
    page = f'https://www.bayern.landtag.de/webangebot2/webangebot/protokolle?execution=e2s1'
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Germany/Bayern/18'
    # dir_download = f"/storage/projects/bagci/data/test"
    prefs = {'download.default_directory': dir_download, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(page)
    time.sleep(2)
    # Cookies
    driver.find_element(By.XPATH, f'//*[@id="mcc-deny"]').click()
    # Enter search date
    date_input = driver.find_element(By.XPATH, f'//*[@id="sitzungsdatumdatumInputDate"]')
    date_input.clear()
    date_input.send_keys("01.01.2018")
    # Search
    driver.find_element(By.XPATH, f'//*[@id="sucheBtn"]').click()
    loading = True
    while loading:
        try:
            driver.find_element(By.XPATH, f'//*[@id="j_id96:0:j_id102"]/a[1]')
            loading = False
        except Exception as ex:
            time.sleep(1)
    all_files = driver.find_elements(By.CLASS_NAME, f'rich-table-row')
    for c, file_i in enumerate(tqdm(all_files, desc="Download Bayern files")):
        try:
            print("h")
            info = file_i.find_elements(By.CLASS_NAME, f'rich-table-cell')
            file_date = info[0].text
            short_date = file_date.replace(".", "")
            short_date = short_date[:4] + short_date[6:]
            file_sitzung = info[1].text
            driver.find_element(By.XPATH, f'//*[@id="j_id96:{c}:j_id102"]/a[1]').click()
            file_saved_name = f"{dir_download}/{file_sitzung.split('.')[0]}PL{short_date}gesendgKopie.pdf"
            while not os.path.exists(file_saved_name):
                time.sleep(0.5)
            time.sleep(1)
            os.makedirs(f"{dir_download}/{file_date.split('.')[-1]}", exist_ok=True)
            new_save_dir = f"{dir_download}/{file_date.split('.')[-1]}/{file_date}_{file_sitzung}.pdf"
            os.rename(file_saved_name, new_save_dir)
        except Exception as ex:
            print(ex)
    print("h")


if __name__ == '__main__':
    downloader()
