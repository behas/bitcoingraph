#!/usr/bin/env python

import csv
import requests


def scrape_page(writer):
    url = 'https://raw.githubusercontent.com/blockchain/Blockchain-Known-Pools/master/pools.json'
    r = requests.get(url)
    payout_addresses = r.json()['payout_addresses']
    for payout_address, info in payout_addresses.items():
        address = payout_address
        tag = info['name']
        link = info['link']
        writer.writerow([address, tag, link])


with open('identities_pools.csv', 'w') as identities_file:
    identities_writer = csv.writer(identities_file)
    identities_writer.writerow(['address', 'tag', 'link'])
    scrape_page(identities_writer)
