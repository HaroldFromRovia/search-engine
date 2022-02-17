import os
import bisect
from collections.abc import Mapping

from core import utils
from core.settings import settings
from crawler import scrapper
from semantic import tokenizer
from semantic.tokenizer import tokenize

INVERTED_INDEX_PATH = os.path.join(settings.RESOURCE_PATH, 'inverted_index.txt')
TF_INDEX_PATH = os.path.join(settings.RESOURCE_PATH, 'tf_index.txt')


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


def termfreq(document: str, tf_dict: dict):
    content = set(tokenize(document))
    for token in tf_dict.keys():
        if token.strip() in content:
            tf_dict[token.strip()] += 1
    return len(content)


def create_tf():
    utils.touch_file(TF_INDEX_PATH)
    tokens = set()
    total_token_count = 0

    with open(tokenizer.TOKENS_PATH, encoding="utf-8") as file:
        for line in file.readlines():
            tokens.add(line.strip())
    tf_dict = dict.fromkeys(tokens, 0)
    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page), encoding="utf-8") as file:
            total_token_count += termfreq(file.read(), tf_dict)
    return tf_dict, total_token_count


def create_inv_index(lemm_token_map):
    utils.touch_file(INVERTED_INDEX_PATH)
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


if __name__ == '__main__':

    lemm_token_map = {}
    with open(tokenizer.LEMMAS_PATH, encoding='utf-8') as file:
        for line in file.readlines():
            values = line.strip().split(' ')
            lemm_token_map[values[0].replace(':', '')] = values[1:]

    index = create_inv_index(lemm_token_map)
    with open(INVERTED_INDEX_PATH, mode='at', encoding='utf-8') as file:
        for key, value in index.items():
            file.write('{} {}\n'.format(key, ' '.join(value)))

    tf_index, count = create_tf()
    test_sum = 0
    with open(TF_INDEX_PATH, mode='at', encoding='utf-8') as file:
        for key, value in tf_index.items():
            test_sum += float(value / count)
            file.write('{} {}\n'.format(key, float(value / count)))

    print(test_sum)