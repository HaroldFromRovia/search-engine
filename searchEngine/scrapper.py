import os
import time

import htmlmin
import scrapy

PAGES_COUNT = 99
BASE_ITERATION = 30000
PATH = '../resources'
BASE_URL = 'https://stackoverflow.com/questions/{}'


def init_urls():
    urls = []
    for i in range(PAGES_COUNT):
        urls.append(BASE_URL.format(i + BASE_ITERATION))
    return urls


class Spider(scrapy.Spider):
    name = "crawler"

    def start_requests(self):
        urls = init_urls()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            time.sleep(3)

    def parse(self, response, **kwargs):
        content = response.xpath('//div[@id="mainbar"]').get()
        minified_content = htmlmin.minify(content, remove_comments=True, remove_all_empty_space=True, reduce_empty_attributes=True)

        filename = response.url.split("/")[-1] + '.html'
        with open(os.path.join(PATH, filename), 'w') as f:
            f.write(minified_content)