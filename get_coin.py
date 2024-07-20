import lxml
import csv
import re
import requests
from bs4 import BeautifulSoup as bs


def update_database():
    url = "https://coinmarketcap.com/"
    response = requests.get(url).text
    soup = bs(response, 'lxml')
    links = []
    find_class = soup.find('table').find_all('a')
    for cl in find_class:
        index = cl.get('href').find('/#markets')
        if index == -1:
            links.append(url+cl.get('href')[1:])

    titles = []
    for r in links:
        detail_resp = requests.get(r).text
        detail_soup = bs(detail_resp, 'lxml')
        try:
            title = detail_soup.find(
                'span', class_='sc-65e7f566-0 lsTl').text[:-1].split(' ')
        except AttributeError:
            pass
        titles.append(title[0])

    with open(f'./coins.csv', 'w', newline='') as out_csv:
        writer = csv.writer(out_csv, delimiter=", ", lineterminator="\r")
        writer.writerow(['Name', 'Link'])
        cnt = 0
        for _ in range(len(titles)):
            writer.writerow([
                titles[cnt],
                links[cnt]
            ])
            cnt += 1


update_database()
