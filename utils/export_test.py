#!/usr/bin/env python

import csv
import requests


def get_block(hash):
    def a_b(a, b):
        return '{}_{}'.format(a, b)
    r = session.get('http://localhost:8332/rest/block/{}.json'.format(hash))
    block = r.json()
    block_writer.writerow([block['hash'], block['height'], block['time']])
    for tx in block['tx']:
        is_coinbase = 'coinbase' in tx['vin'][0]
        transaction_writer.writerow([tx['txid'], is_coinbase])
        rel_block_tx_writer.writerow([block['hash'], tx['txid']])
        if not is_coinbase:
            for vin in tx['vin']:
                rel_input_writer.writerow([tx['txid'], a_b(vin['txid'], vin['vout'])])
        for vout in tx['vout']:
            output_writer.writerow([a_b(tx['txid'], vout['n']), vout['n'],
                                    vout['value'], vout['scriptPubKey']['type']])
            rel_tx_output_writer.writerow([tx['txid'], a_b(tx['txid'], vout['n'])])
            if 'addresses' in vout['scriptPubKey']:
                for address in vout['scriptPubKey']['addresses']:
                    address_writer.writerow([address])
                    rel_output_address_writer.writerow([a_b(tx['txid'], vout['n']), address])
    return block['nextblockhash']


def write_header(filename, row):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(row)


write_header('blocks_header.csv', ['hash:ID(Block)', 'height:int', 'timestamp:int'])
write_header('transactions_header.csv', ['txid:ID(Transaction)', 'coinbase:boolean'])
write_header('outputs_header.csv', ['txid_n:ID(Output)', 'n:int', 'value:double', 'type'])
write_header('addresses_header.csv', ['address:ID(Address)'])
write_header('rel_block_tx_header.csv', [':START_ID(Block)', ':END_ID(Transaction)'])
write_header('rel_tx_output_header.csv', [':START_ID(Transaction)', ':END_ID(Output)'])
write_header('rel_input_header.csv', [':END_ID(Transaction)', ':START_ID(Output)'])
write_header('rel_output_address_header.csv', [':START_ID(Output)', ':END_ID(Address)'])


with open('blocks.csv', 'w') as blocks_file,\
        open('transactions.csv', 'w') as transactions_file,\
        open('outputs.csv', 'w') as outputs_file,\
        open('addresses.csv', 'w') as addresses_file,\
        open('rel_block_tx.csv', 'w') as rel_block_tx_file,\
        open('rel_tx_output.csv', 'w') as rel_tx_output_file,\
        open('rel_input.csv', 'w') as rel_input_file,\
        open('rel_output_address.csv', 'w') as rel_output_address_file:
    block_writer = csv.writer(blocks_file)
    transaction_writer = csv.writer(transactions_file)
    output_writer = csv.writer(outputs_file)
    address_writer = csv.writer(addresses_file)
    rel_block_tx_writer = csv.writer(rel_block_tx_file)
    rel_tx_output_writer = csv.writer(rel_tx_output_file)
    rel_input_writer = csv.writer(rel_input_file)
    rel_output_address_writer = csv.writer(rel_output_address_file)

    block_hash = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
    with requests.Session() as session:
        for counter in range(0, 1001):
            block_hash = get_block(block_hash)
