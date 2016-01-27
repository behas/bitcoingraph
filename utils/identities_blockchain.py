#!/usr/bin/env python

from bs4 import BeautifulSoup
import csv
import requests
import urllib


def scrape_page(writer, list_key, offset):
    r = requests.get('https://blockchain.info/de/tags',
                     params={'filter': list_key, 'offset': offset})
    soup = BeautifulSoup(r.text, 'html.parser')
    for tr in soup.tbody.find_all('tr'):
        if tr.img['src'].endswith('green_tick.png'):
            tds = tr.find_all('td')
            address = tds[0].get_text()
            tag = tds[1].get_text()
            link = urllib.parse.unquote(tds[2].a['href'].rpartition('=')[2])
            writer.writerow([address, tag, link])
    page_links = soup.find_all('div', class_='pagination')[0].find_all('a')
    last_offset = int(page_links[-2]['href'].rpartition('=')[2])
    return last_offset


with open('identities.csv', 'w') as identities_file:
    identities_writer = csv.writer(identities_file)
    identities_writer.writerow(['address', 'tag', 'link'])
    for list_key in [8, 16, 2, 4]:
        last_offset = scrape_page(identities_writer, list_key, 0)
        for off in range(200, last_offset + 1, 200):
            print('(list {}) scrape identity {} of {}'.format(list_key, off, last_offset))
            scrape_page(identities_writer, list_key, off)
