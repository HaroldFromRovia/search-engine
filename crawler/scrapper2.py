import requests
import time

PAGES_COUNT = 99
BASE_ITERATION = 30000
PATH = '../html'
BASE_URL = 'https://stackoverflow.com/questions/{}'

counter = 0
if __name__ == '__main__':
    file = open('index.txt', 'w')
    for i in range(1000):
        r = requests.get(BASE_URL.format(130000 + i), allow_redirects=True)

        if r.status_code == 200:
            open('../html/{}.html'.format(i), 'wb').write(r.content)
            file.write('{id}.html https://stackoverflow.com/questions/{id}\n'.format(id=i))
            print(i)
            counter += 1
        time.sleep(1)
        if counter > 150:
            break

    file.close()
