import os
import bisect
from collections.abc import Mapping

from core import utils
from core.settings import settings
from crawler import scrapper
from semantic import tokenizer

INVERTED_INDEX_PATH = os.path.join(settings.RESOURCE_PATH, 'inverted_index.txt')


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


def create_inv_index(lemm_token_map):
    utils.touch_file(INVERTED_INDEX_PATH)
    index = {}
    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page)) as page_file:
            content = page_file.read()
            for key, value in lemm_token_map.items():
                for token in value:
                    if token in content:
                        index_page = index.get(key, [])
                        index_page.append(os.path.basename(page_file.name).split('.')[0])

                        index[key] = index_page
    return index


if __name__ == '__main__':

    lemm_token_map = {}
    with open(tokenizer.LEMMAS_PATH) as file:
        for line in file.readlines():
            values = line.strip().split(' ')
            lemm_token_map[values[0].replace(':', '')] = values[1:]

    index = create_inv_index(lemm_token_map)
    with open(INVERTED_INDEX_PATH, mode='at', encoding='utf-8') as file:
        for key, value in index.items():
            file.write('{} {}\n'.format(key, ' '.join(value)))
