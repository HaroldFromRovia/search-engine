import os
import time

import scrapy

PAGES_COUNT = 150
BASE_ITERATION = 30000
PATH = './resources'
BASE_URL = 'https://stackoverflow.com/questions/{}'


def init_urls():
    urls = []
    for i in range(PAGES_COUNT):
        urls.append(BASE_URL.format(i + BASE_ITERATION))
    return urls


class Spider(scrapy.Spider):
    start_urls = init_urls()
    name = "crawler"

    def start_requests(self):
        urls = init_urls()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            time.sleep(5)

    def parse(self, response, **kwargs):
        filename = response.url.split("/")[-1] + '.html'
        with open(os.path.join(PATH, filename), 'wb') as f:
            f.write(response.body)
