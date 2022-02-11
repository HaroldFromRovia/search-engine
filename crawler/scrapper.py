import os
import time

import htmlmin
import scrapy

# To avoid getting banned by site for spamming. Value in seconds
REQUEST_DELAY = 1

BASE_URL = 'https://stackoverflow.com/questions/{}'
DEFAULT_ENCODING = "UTF-8"

PAGES_COUNT = 1
BASE_ITERATION = 30000

RESOURCE_PATH = '../resources'
INDEX_FILE_NAME = "index.txt"
PAGES_PATH = 'pages'
INDEX_FILE_PATH = os.path.join(RESOURCE_PATH, INDEX_FILE_NAME)
PAGES_PATH = os.path.join(RESOURCE_PATH, PAGES_PATH)


def init_urls():
    urls = []

    for i in range(PAGES_COUNT):
        url = BASE_URL.format(i + BASE_ITERATION)
        urls.append(url)

    return urls


def init_folders():
    if not os.path.exists(PAGES_PATH):
        os.makedirs(PAGES_PATH, exist_ok=True)
    if not os.path.isfile(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, 'w'): pass


def append_to_index(index: str, url):
    with open(INDEX_FILE_PATH, 'a') as index_file:
        index_file.write(index + ' ' + url + '\n')


class Spider(scrapy.Spider):
    name = "crawler"

    def __init__(self):
        super(Spider, self).__init__()

        self.urls = init_urls()
        self.index_iteration = 0
        init_folders()

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)
            time.sleep(REQUEST_DELAY)

    def parse(self, response, **kwargs):
        content = response.xpath('//div[@id="mainbar"]').get()
        minified_content = htmlmin.minify(content, remove_comments=True, remove_all_empty_space=True,
                                          reduce_empty_attributes=True)

        filename = str(self.index_iteration) + '.html'
        with open(os.path.join(PAGES_PATH, filename), 'w', encoding=DEFAULT_ENCODING) as f:
            f.write(minified_content)

        append_to_index(str(self.index_iteration), response.url)
        self.index_iteration += 1
