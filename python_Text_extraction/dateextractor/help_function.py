import json
import os
import gzip
import json
from typing import Tuple, List

from tqdm import tqdm

set_files = set()


def get_all_path_files(path_dir: str, end_file: str):
    global set_files
    for file in os.scandir(path_dir):
        if file.is_dir():
            get_all_path_files(file, end_file)
        elif (str(file.path)).endswith(f"{end_file}"):
            set_files.add(str(file.path))


def get_set_files():
    global set_files
    return set_files


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


def reset_set_files():
    global set_files
    set_files = set()


def get_difference_path_data(txt_path: str, xmi_path: str, output_name: str):
    global set_files
    get_all_path_files(txt_path, ".txt")
    txt_set = set_files
    txt_dict = {}
    for i in txt_set:
        name = i.split("/")[-1]
        txt_dict[name] = i
    set_files = set()
    get_all_path_files(xmi_path, ".xmi.gz")
    xmi_set = set_files
    xmi_dict = {}
    for i in xmi_set:
        name = i.split("/")[-1].split(".xmi")[0]
        xmi_dict[name] = i
    dif = set(txt_dict.keys()).difference(set(xmi_dict.keys()))
    dif_list = []
    for i in dif:
        if i in txt_dict:
            dif_list.append(txt_dict[i])
    with open(f"{os.path.dirname(txt_path)}/{output_name}", "w", encoding="UTF-8") as json_file:
        json.dump(dif_list, json_file, indent=2, ensure_ascii=True)


def write_text(text_data, data_dir, gzip_save=False):
    os.makedirs(os.path.dirname(data_dir), exist_ok=True)
    if gzip_save:
        with gzip.open(data_dir, "wt", encoding="UTF-8") as txt_file:
            txt_file.write(text_data)
    else:
        with open(data_dir, "w", encoding="UTF-8") as txt_file:
            txt_file.write(text_data)


def get_network_tweets(network_tweets: dict, read_name="text") -> Tuple[List[str], List[str]]:
    list_ids = []
    list_tweets = []
    for tweet_id in tqdm(network_tweets, desc="Get all text of tweets in the Network"):
        text = network_tweets[tweet_id][read_name]
        list_ids.append(tweet_id)
        list_tweets.append(text)
    return list_tweets, list_ids


def load_html(path_dir: str)->str:
    with open(path_dir, "r") as txt:
        return txt.read()


def load_text(path_dir: str)->str:
    with open(path_dir, "r", encoding="UTF-8") as txt:
        return txt.read()


if __name__ == "__main__":
    category = ["Quantitative-Biology", "Quantitative-Finance", "Economy"]
    path_txt = "/resources/corpora/Arxiv/java_cleaned"
    path_xmi = "/resources/corpora/Arxiv/xmi_java"
    for cat in ["Economy"]:
        get_difference_path_data(f"{path_txt}/{cat}", f"{path_xmi}/{cat}", f"{cat}_dif_txt_to_xmi.json")