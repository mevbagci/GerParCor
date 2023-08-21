import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import urllib.request
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select


def dowload_pdf(file_name, url):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    response = urllib.request.urlopen(url)
    file = open(file_name, 'wb')
    file.write(response.read())
    file.close()


def downloader():
    chrome_options = webdriver.ChromeOptions()
    page = f'https://www.land-oberoesterreich.gv.at/ltgspsuche.htm'
    dir_download = f'/storage/projects/abrami/GerParCor/pdf/Austria/Oberoestereich'
    # dir_download = f"/storage/projects/bagci/data/test"
    prefs = {'download.default_directory': dir_download, 'intl.accept_languages': 'de,de_DE'}
    os.makedirs(dir_download, exist_ok=True)
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(page)
    time.sleep(2)
    paths = ['//*[@id="inhalt"]/div[2]/ul[1]/li[1]/span/a', '//*[@id="inhalt"]/div[2]/ul[1]/li[2]/span/a',
             '//*[@id="inhalt"]/div[2]/ul[1]/li[3]/span/a', '//*[@id="inhalt"]/div[2]/ul[1]/li[4]/span/a']
    data_paths = {}
    for path_i in paths:
        data_path = driver.find_element(By.XPATH, path_i)
        data_path_name = data_path.get_attribute("href")
        path_var = ""
        path_var += f"{data_path.text}"
        data_paths[path_var] = data_path_name
    for path_var in data_paths:
        driver.get(data_paths[path_var])
        time.sleep(2)
        all_links = []
        for element_i in driver.find_elements(By.CLASS_NAME, 'liste-extra'):
            for links in element_i.find_elements(By.TAG_NAME, "a"):
                link_i = links.get_attribute("href")
                if link_i is not None:
                    all_links.append(link_i)
        print("Start_downloading")
        for i in all_links:
            driver.get(i)
            time.sleep(2)
            var = ('G', 'E', 'E', 'K')
            file_name = str(hash(var))
            for intern_link in driver.find_elements(By.CLASS_NAME, "beilagenElement"):
                if "Volltext" in intern_link.text:
                    pdf_link = intern_link.find_elements(By.TAG_NAME, "a")[0].get_attribute("href")
                    if pdf_link is not None:
                        # driver.get(pdf_link)
                        dowload_pdf(f"{dir_download}/{path_var}/{file_name}.pdf", pdf_link)
                else:
                    file_name = intern_link.text


if __name__ == '__main__':
    downloader()
