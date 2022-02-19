import math
import os
import bisect
import time
from collections.abc import Mapping

from core import utils
from core.settings import settings
from crawler import scrapper
from semantic import tokenizer
from semantic.tokenizer import tokenize, lemmatize

INVERTED_INDEX_PATH = os.path.join(settings.RESOURCE_PATH, 'inverted_index.txt')
TF_IDF_TOKEN_INDEX_PATH = os.path.join(settings.RESOURCE_PATH, 'tf-idf_token_index.txt')
TF_IDF_LEMMA_INDEX_PATH = os.path.join(settings.RESOURCE_PATH, 'tf-idf_lemma_index.txt')
TF_IDF_LEMMA_INDEX_SEPARATED_PATH = os.path.join(settings.RESOURCE_PATH, 'tf-idf_lemma_index_separated.txt')
LEMMAS_PATH = os.path.join(settings.RESOURCE_PATH, 'lemmas.txt')


class Index(Mapping):
    def __init__(self, contents):
        self._list = sorted(contents)

    def __iter__(self):
        return (k for (k, _) in self._list)

    def __contains__(self, k):
        i = bisect.bisect_left(self._list, (k, None))
        return i < len(self._list) and self._list[i][0] == k

    def __len__(self):
        return len(self._list)

    def __getitem__(self, k):
        i = bisect.bisect_left(self._list, (k, []))
        if i >= len(self._list): raise KeyError(k)
        return self._list[i][1]


def create_files():
    utils.touch_file(INVERTED_INDEX_PATH)
    utils.touch_file(TF_IDF_TOKEN_INDEX_PATH)
    utils.touch_file(TF_IDF_LEMMA_INDEX_PATH)


def compute_idf(token_pages_map, documents_count):
    idf_index = {}
    for key, value in token_pages_map.items():
        idf_index[key] = math.log10(documents_count / float(len(value)))

    return idf_index


def termfreq(document: str, tf_dict: dict):
    content = set(tokenize(document))
    for token in tf_dict.keys():
        if token.strip() in content:
            tf_dict[token.strip()] += 1
    return len(content)


def termfreq_for_lemmas(document: str, tf_dict: dict):
    lemmas = lemmatize(set(tokenize(document))).keys()
    for token in tf_dict.keys():
        if token.strip() in lemmas:
            tf_dict[token.strip()] += 1
    return len(lemmas)


def create_tf_for_lemmas(lemmas: set):
    total_lemma_count = 0

    tf_dict = dict.fromkeys(lemmas, 0)
    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page), encoding="utf-8") as file:
            total_lemma_count += termfreq_for_lemmas(file.read(), tf_dict)
    return tf_dict, total_lemma_count


def create_tf_for_each_page(lemmas: set):
    tf = dict.fromkeys([page for page in os.listdir(scrapper.PAGES_PATH)], 0)

    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page), encoding="utf-8") as file:
            tf_dict = dict.fromkeys(lemmas, 0)
            termfreq_for_lemmas(file.read(), tf_dict)
            tf[page] = tf_dict
    return tf



def create_tf(tokens: set):
    total_token_count = 0

    tf_dict = dict.fromkeys(tokens, 0)
    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page), encoding="utf-8") as file:
            total_token_count += termfreq(file.read(), tf_dict)
    return tf_dict, total_token_count


def create_inv_index(lemm_token_map):
    index = {}
    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page), encoding='utf-8') as page_file:
            content = set(tokenize(page_file.read()))
            for key, value in lemm_token_map.items():
                for token in value:
                    if token.strip() in content:
                        index_page = index.get(key, [])
                        index_page.append(os.path.basename(page_file.name).split('.')[0])

                        index[key.strip()] = index_page
    return index


def extract_tokens(tokens):
    index = {}
    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page), encoding='utf-8') as page_file:
            content = set(tokenize(page_file.read()))
            for token in tokens:
                if token.strip() in content:
                    index_page = index.get(token, [])
                    index_page.append(os.path.basename(page_file.name).split('.')[0])

                    index[token.strip()] = index_page
    return index



def get_unique_lemmas():
    file = open(LEMMAS_PATH)

    lemmas = set()

    for lemma in file:
        lemmas.add(lemma.split(':')[0])

    return lemmas


if __name__ == '__main__':
    start_time = time.time()
    create_files()
    lemm_token_map = {}

    tokens = set()
    with open(tokenizer.TOKENS_PATH, encoding="utf-8") as file:
        for line in file.readlines():
            tokens.add(line.strip())

    with open(tokenizer.LEMMAS_PATH, encoding='utf-8') as file:
        for line in file.readlines():
            values = line.strip().split(' ')
            lemm_token_map[values[0].replace(':', '')] = values[1:]

    inverted_index = create_inv_index(lemm_token_map)
    with open(INVERTED_INDEX_PATH, mode='at', encoding='utf-8') as file:
        for key, value in inverted_index.items():
            file.write('{} {}\n'.format(key, ' '.join(value)))

    tf_token_index, tf_token_count = create_tf(tokens)
    tf_lemma_map, tf_lemma_count = create_tf_for_lemmas(set(lemm_token_map.keys()))

    token_pages_map = extract_tokens(tokens)
    idf_token_map = compute_idf(token_pages_map, settings.PAGES_COUNT)
    idf_lemma_map = compute_idf(inverted_index, settings.PAGES_COUNT)

    with open(TF_IDF_TOKEN_INDEX_PATH, mode='at', encoding='utf-8') as file:
        for key, value in tf_token_index.items():
            file.write('{} {} {}\n'.format(key, idf_token_map.get(key), idf_token_map.get(key) * value))

    with open(TF_IDF_LEMMA_INDEX_PATH, mode='at', encoding='utf-8') as file:
        for key, value in tf_lemma_map.items():
            file.write('{} {} {}\n'.format(key, idf_lemma_map.get(key), idf_lemma_map.get(key) * value))


    tf_lemma_map_separated = create_tf_for_each_page(set(lemm_token_map.keys()))

    with open(TF_IDF_LEMMA_INDEX_SEPARATED_PATH, mode='at', encoding='utf-8') as file:
        for document, lemmas in tf_lemma_map_separated.items():
            for lemma, tf in lemmas.items():
                a = tf
                b = idf_lemma_map.get(key)
                file.write('{} {} {}\n'.format(document, lemma, idf_lemma_map.get(key) * tf))

    print("--- %s seconds ---" % (time.time() - start_time))
