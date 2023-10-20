import json
import argparse
import multiprocessing
import pkg_resources
from symspellpy import SymSpell, Verbosity
import os
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial

set_files = set()


def spellchecker(input_txt_dir: str, speller: SymSpell, spell_object_name: str):
    """
    :param input_txt_dir: Path of the txt-file
    :param speller: SymSpell for checking the spelling mistakes
    :param spell_object_name: Modifier for the output name
    :return: Dictionary of the qualities
    """
    right = 0
    wrong = 0
    unknown = 0
    number_of_words = 0
    skipped_words = 0
    all_words = 0
    quality_good, quality_good_unknown = 0.0, 0.0
    quality = 0.0
    try:
        with open(input_txt_dir, "r", encoding="UTF-8") as text_file:
            text = text_file.read()
            text = text.replace("\n", " ")
        for word in text.split():
            #  and not "ſ" in word:
            all_words += 1
            if word.isalnum() and not word.isdigit():
                number_of_words += 1
                suggestions = speller.lookup(word.lower(), Verbosity.CLOSEST, max_edit_distance=2)
                if suggestions:
                    if suggestions[0].term == word.lower():
                        right += 1
                    else:
                        wrong += 1
                else:
                    unknown += 1
            else:
                skipped_words += 1
        if right != 0 and wrong != 0:
            quality_good = right / (wrong + right)
            quality_good_unknown = right / number_of_words
            quality = right / (wrong + right + unknown + skipped_words)
        elif wrong == 0:
            quality_good, quality_good_unknown = 1.0, 1.0
            quality = 1.0
        elif right:
            quality_good, quality_good_unknown = 0.0, 0.0
            quality = 0.0
        file_base_name = str(os.path.basename(input_txt_dir))
        name_data = f"{spell_object_name}_{file_base_name}"
        dict_spellcheck_text = {"name": name_data,
                                "right_number": right,
                                "wrong_number": wrong,
                                "unknown_number": unknown,
                                "skipped_words": skipped_words,
                                "number_of_words": number_of_words,
                                "quality_good": quality_good,
                                "quality_good_unknown": quality_good_unknown,
                                "quality": quality,
                                "all_words": all_words,
                                }
        return dict_spellcheck_text
    except Exception as ex:
        print(f"{input_txt_dir}, Error: {ex}")


def multiprocessing_spellchecker(in_txt_dir: str, in_dir_speller: str, spell_object_name: str, out_dir: str):
    """
    :param in_txt_dir: Directory of all txt-files
    :param in_dir_speller: Name of the SymSpell word lexicon
    :param spell_object_name: Modifier for the output name
    :param out_dir: Location for the output
    :return:
    """
    # in_dir_speller = f"de-100k.txt"
    try:
        sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        dictionary_path = pkg_resources.resource_filename(
            "symspellpy", in_dir_speller
        )
        sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
    except Exception as ex:
        print(f"{in_dir_speller}, Error: {ex}")
        exit()
    global set_files
    set_files = set()
    get_all_path_files(in_txt_dir, ".txt")
    files = list(set_files)
    part_func = partial(spellchecker, speller=sym_spell, spell_object_name=spell_object_name)
    pool = Pool(multiprocessing.cpu_count() - 1)
    result = list(tqdm(pool.imap_unordered(part_func, files),
                       desc=f"Spellchecking {spell_object_name}: {in_txt_dir.split('/')[-1]}", total=len(files)))
    pool.close()
    pool.join()
    os.makedirs(out_dir, exist_ok=True)
    out_name_dir = f"{out_dir}/{spell_object_name}_spellchecking.json"
    right_number = 1
    wrong_number = 1
    for i in result:
        right_number += i["right_number"]
        wrong_number += i["wrong_number"]
    all_good_quality = right_number / (wrong_number + right_number)
    out_all = out_name_dir.replace(".json", "_all_together.txt")
    print(f"Output: {out_all}")
    with open(out_name_dir, "w", encoding="UTF-8") as out_name_dir:
        json.dump(list(result), out_name_dir, indent=2)
    with open(out_all, "w", encoding="UTF-8") as text_file:
        text_file.write(f"Good_quality\tright_number\twrong_number\n")
        text_file.write(f"{all_good_quality}\t{right_number}\t{wrong_number}\n")


def get_all_path_files(path_dir: str, end_file: str):
    """
    :param path_dir: directory path for searching file paths
    :param end_file: which files should be search (txt-data => .txt)
    :return:
    """
    global set_files
    for file in os.scandir(path_dir):
        if file.is_dir():
            get_all_path_files(file, end_file)
        elif (str(file.path)).endswith(f"{end_file}"):
            set_files.add(str(file.path))


def summary_result_spellcheck(input_dir_results: str, end_with: str, spell_object_name: str = "SpellChecking"):
    """
    :param input_dir_results: Directory of the spellchecking result
    :param end_with: Data format of the results normally .txt
    :param spell_object_name: Modifier for the output name
    :return:
    """
    global set_files
    set_files = set()
    get_all_path_files(input_dir_results, end_with)
    files = list(set_files)
    quality_sum = 0
    number_right = 0
    number_wrong = 0
    skipped_words = 0
    all_words = 0
    out_first_line = f"Good_quality\tright_number\twrong_number\n"
    if end_with ==".json":
        out_dir_name = f"{input_dir_results}/{spell_object_name}_all_quality_out.json"
        right = 0
        wrong = 0
        unknown = 0
        number_words = 0
        for file_dir in tqdm(files, desc=f"Put all qualities together of {spell_object_name}"):
            with open(file_dir, "r", encoding="UTF-8") as json_file:
                if file_dir == out_dir_name:
                    continue
                file_jsons = json.load(json_file)
                for data_i in file_jsons:
                    right += data_i["right_number"]
                    wrong += data_i["wrong_number"]
                    unknown += data_i["unknown_number"]
                    number_words += data_i["number_of_words"]
                    all_words += data_i["all_words"]
                    skipped_words += data_i["skipped_words"]
        quality_good = right/(right+wrong)
        quality_unknown = right/number_words
        quality = right/all_words
        percent_right = right/number_words
        percent_wrong = wrong/number_words
        percent_unknown = unknown/number_words
        percent_right_with_skipped = right/all_words
        percent_wrong_with_skipped = wrong/all_words
        percent_unknown_with_skipped = unknown/all_words
        data_sum = {
            "right_number": right,
            "wrong_number": wrong,
            "unknown_number": unknown,
            "number_of_words": number_words,
            "skipped_words": skipped_words,
            "all_words": all_words,
            "quality_good": quality_good,
            "quality_unknown": quality_unknown,
            "quality": quality,
            "percent_right": percent_right,
            "percent_wrong": percent_wrong,
            "percent_unknown": percent_unknown,
            "percent_right_with_skipped": percent_right_with_skipped,
            "percent_wrong_with_skipped": percent_wrong_with_skipped,
            "percent_unknown_with_skipped": percent_unknown_with_skipped,
            "text": f"Good_quality\tUnknown quality\tunknown words\tright words\twrong words\n"
                    f"{quality_good}%\t{quality_unknown}%\t{unknown/number_words}%\t{right/number_words}%\t{wrong/number_words}"
        }
        with open(out_dir_name, "w", encoding="UTF-8") as json_file:
            json.dump(data_sum, json_file, indent=2)
    else:
        for file_dir in tqdm(files, desc=f"Put all qualities together of {spell_object_name}"):
            with open(file_dir, "r", encoding="UTF-8") as txt_file:
                info_out = txt_file.readlines()[1].split()
                quality_sum += float(info_out[0])
                number_right += int(info_out[1])
                number_wrong += int(info_out[2].replace("\n", ""))
        quality_federal_state = quality_sum / len(files)
        out_dir_name = f"{input_dir_results}/{spell_object_name}_all_quality_out.txt"
        with open(out_dir_name, "w", encoding="UTF-8") as out_text_file:
            out_text_file.write(out_first_line)
            out_text_file.write(f"{quality_federal_state}\t{number_right}\t{number_wrong}")


if __name__ == "__main__":
    path_txt = f"/storage/projects/abrami/GerParCor/txt"
    path_out = f"/storage/projects/abrami/GerParCor/spellchecking"
    # BadenWuertemmberg
    path_baden = f"{path_txt}/Germany/BadenWuertemmberg"
    all_path_baden = [
        0, 1, 2, 3, 4, 5, 6, 7, 8
    ]
    # for i in all_path_baden:
    #     out_i = f"{path_out}/Germany/BadenWuertemmberg/{i}"
    #     path_i = f"{path_baden}/{i}"
    #     multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)
    # ocr_path = [
    #     "older"
    # ]
    # for i in ocr_path:
    #     out_i = f"{path_out}/Germany/BadenWuertemmberg/{i}"
    #     path_i = f"{path_baden}/{i}"
    #     multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)
    #
    # #Niederaustria
    # path_nieder = f"{path_txt}/Austria/Niederoestereich"
    # niederaustria = [
    #     "IV. Gesetzgebungsperiode", "V. Gesetzgebungsperiode", "VI. Gesetzgebungsperiode", "VII. Gesetzgebungsperiode"
    # ]
    # for i in niederaustria:
    #     out_i = f"{path_out}/Austria/Niederoestereich/{i}"
    #     path_i = f"{path_nieder}/{i}"
    #     multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)
    #
    # # steiermark
    # path_steiermark = f"{path_txt}/Austria/Steiermark"
    # steiermark = [
    #         "1848", "1861 - 1866 (Periode I)", "1867 - 1869 (Periode II)", "1870 (Periode III)", "1871 - 1877 (Periode IV)", "1878 - 1883 (Periode V)", "1884 - 1889 (Periode VI)",
    #         "1890 - 1896 (Periode VII)", "1896 - 1902 (Periode VIII)", "1902 - 1908 (Periode IX)", "1909 - 1914 (Periode X)", "1918 - 1919", "1919 - 1920", "1920 - 1923 (Periode I)",
    #         "1923 - 1927 (Periode II)", "1927 - 1930 (Periode III)", "1931 - 1934 (Periode IV)", "1934 - 1938 (Periode V)"
    #     ]
    #
    # for i in steiermark:
    #     out_i = f"{path_out}/Austria/Steiermark/{i}"
    #     path_i = f"{path_steiermark}/{i}"
    #     multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)
    #
    # tirol = list(range(1921, 1970))
    # path_tirol = f"{path_txt}/Austria/Tirol/Sitzungsbericht"
    # for i in tirol:
    #     out_i = f"{path_out}/Austria/Tirol/Sitzungsbericht/{i}"
    #     path_i = f"{path_tirol}/{i} Periode"
    #     if os.path.exists(path_i):
    #         multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)
    #
    # tirol_kurz = list(range(1865, 1930))
    # path_tirol_kurz = f"{path_txt}/Austria/Tirol/Kurzprotokoll"
    # for i in tirol_kurz:
    #     out_i = f"{path_out}/Austria/Tirol/Kurzprotokoll/{i}"
    #     path_i = f"{path_tirol_kurz}/{i} Periode"
    #     if os.path.exists(path_i):
    #         multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)
    #
    # #Bundesrat
    # older_input = [
    #     "I", "II", "III", "IV",
    # ]
    # path_bundesrat = f"{path_txt}/Austria/Bundesrat"
    # for i in older_input:
    #     out_i = f"{path_out}/Austria/Bundesrat/{i}"
    #     path_i = f"{path_bundesrat}/{i}"
    #     multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)

    # Oberoesterreich
    # path_ober = f"{path_txt}/Austria/Oberoestereich"
    # out_ober = f"{path_txt}/Austria/Oberoestereich"
    # oberautria = ["18", "19", "20", "21", "22", "23",
    #                   # "XXIX", "XXVI", "XXVII" "XVIII"
    #                   ]
    # oberautria_old = [16, 17]
    # for i in oberautria:
    #     out_i = f"{path_out}/Austria/Oberoestereich/{i}"
    #     path_i = f"{path_ober}/{i}._Gesetzgebungsperiode"
    #     multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)
    # for i in oberautria_old:
    #     out_i = f"{path_out}/Austria/Oberoestereich/{i}"
    #     path_i = f"{path_ober}/{i}._Gesetzgebungsperiode"
    #     multiprocessing_spellchecker(path_i, "de-100k.txt", f"Symspell", out_i)

    #Spellchecking
    #Baden
    summary_result_spellcheck(f"{path_out}/Germany/BadenWuertemmberg/Fraktur", ".json")
    summary_result_spellcheck(f"{path_out}/Germany/BadenWuertemmberg/Non-Fraktur", ".json")

    summary_result_spellcheck(f"{path_out}/Austria/Bundesrat/Fraktur", ".json")
    summary_result_spellcheck(f"{path_out}/Austria/Niederoestereich/Non-Fraktur", ".json")
    summary_result_spellcheck(f"{path_out}/Austria/Oberoestereich/Non-Fraktur", ".json")
    summary_result_spellcheck(f"{path_out}/Austria/Oberoestereich/Fraktur", ".json")
    summary_result_spellcheck(f"{path_out}/Austria/Steiermark/Fraktur", ".json")
    summary_result_spellcheck(f"{path_out}/Austria/Tirol/Fraktur", ".json")


    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-p", "--path_directory", help="Path to the directory with the .txt files")
    # parser.add_argument("-s", "--sym_speller", default="de-100k.txt", help="Name of the word lexicon for SymSpellpy")
    # parser.add_argument("-o", "--out", default="symspell_spellcheck", help="Directory path for the outputs of the spell checking")
    # parser.add_argument("-m", "--name_modifier", default="Symspell", help="Modify the output name")
    # args = parser.parse_args()
    # multiprocessing_spellchecker(in_txt_dir=args.path_directory, in_dir_speller=args.sym_speller, spell_object_name=args.name_modifier, out_dir=args.out)

