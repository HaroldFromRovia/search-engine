import os

import requests
import time

PAGES_COUNT = 100
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


page_counter = 0
if __name__ == '__main__':
    init_folders()

    with open(INDEX_FILE, 'w') as file:
        for i in range(1000):
            r = requests.get(BASE_URL.format(BASE_ITERATION + i), allow_redirects=True)

            if r.status_code == 200:
                open(os.path.join(PAGES_PATH, '{}.html'.format(i)), 'wb').write(r.content)
                file.write('{id}.html {url}\n'.format(id=i, url=r.url))
                page_counter += 1
            else:
                print('Request {url} failed with {code} code'.format(code=r.status_code, url=r.url))
            time.sleep(REQUEST_DELAY)
            if page_counter >= PAGES_COUNT:
                break
