import os.path

import nltk

from core import utils
from core.settings import settings
from crawler import scrapper

NLTK_PACKAGES = ['tokenizers/punkt', 'corpora/stopwords']
TOKENS_PATH = os.path.join(settings.RESOURCE_PATH, 'tokens.txt')


def scan_nltk_packages():
    for package in NLTK_PACKAGES:
        try:
            nltk.find(package)
        except Exception:
            nltk.download(package.split('/')[1])


def tokenize():
    tokens = set()

    for page in os.listdir(scrapper.PAGES_PATH):
        with open(os.path.join(scrapper.PAGES_PATH, page)) as file:
            for line in file:
                tokens.update(nltk.word_tokenize(line))
    return [token.lower() for token in tokens if token.isalpha()]


if __name__ == '__main__':
    utils.touch_file(TOKENS_PATH)
    scan_nltk_packages()
    tokens = tokenize()

    with open(TOKENS_PATH, mode='wt', encoding='utf-8') as file:
        file.write('\n'.join(tokens))
