import os

import htmlmin
import requests
import time

from bs4 import BeautifulSoup

PAGES_COUNT = 1
BASE_ITERATION = 30000
# In seconds
REQUEST_DELAY = 1
RESOURCE_PATH = '../resources'
PAGES_PATH = os.path.join(RESOURCE_PATH, 'html')
INDEX_FILE = os.path.join(RESOURCE_PATH, 'index.txt')
BASE_URL = 'https://stackoverflow.com/questions/{}'


def init_folders():
    if not os.path.exists(PAGES_PATH):
        os.makedirs(PAGES_PATH, exist_ok=True)
    if not os.path.isfile(INDEX_FILE):
        with open(INDEX_FILE, 'w'): pass


def minify(response):
    minified_content = htmlmin.minify(response.text,
                                      remove_comments=True,
                                      remove_all_empty_space=True,
                                      reduce_empty_attributes=True)
    return minified_content


def extract(body):
    soup = BeautifulSoup(body, "html.parser")
    content = []

    comments = soup.find_all('span', class_='comment-copy')
    header = soup.find("div", id="question-header").find("h1")
    tags = set(soup.select('a[class*="post-tag"]'))
    questions_and_answers = soup.find_all("div", class_='s-prose js-post-body')

    content.append(header.get_text())
    for el in tags:
        content.append(el.get_text())
    for el in questions_and_answers:
        content.append(el.get_text())
    for el in comments:
        content.append(el.get_text())

    return content


page_counter = 0
if __name__ == '__main__':
    init_folders()

    with open(INDEX_FILE, 'w') as file:
        for i in range(1000):
            response = requests.get(BASE_URL.format(BASE_ITERATION + i), allow_redirects=True)

            if response.status_code == 200:
                minified = minify(response)
                extracted = ' '.join(extract(minified))

                open(os.path.join(PAGES_PATH, '{}.txt'.format(i)), 'w').write(extracted)
                file.write('{id}.txt {url}\n'.format(id=i, url=response.url))
                page_counter += 1
            else:
                print('Request {url} failed with {code} code'.format(code=response.status_code, url=response.url))
            time.sleep(REQUEST_DELAY)
            if page_counter >= PAGES_COUNT:
                break
