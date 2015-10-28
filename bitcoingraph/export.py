import csv
import os
import requests


def export(number_of_blocks, start_block_hash, output_path=None,
           plain_header=False, separate_header=True, progress=None):
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
        if separate_header:
            filename += '_header'
        with open(get_path(filename), 'w') as f:
            writer = csv.writer(f)
            if plain_header:
                header = [entry.partition(':')[0] for entry in row]
            else:
                header = row
            writer.writerow(header)

    def get_path(filename):
        return os.path.join(output_path, filename + '.csv')

    if output_path is None:
        output_path = 'blocks_{}_{}'.format(number_of_blocks, start_block_hash[60:])
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    write_header('blocks', ['hash:ID(Block)', 'height:int', 'timestamp:int'])
    write_header('transactions', ['txid:ID(Transaction)', 'coinbase:boolean'])
    write_header('outputs', ['txid_n:ID(Output)', 'n:int', 'value:double', 'type'])
    write_header('addresses', ['address:ID(Address)'])
    write_header('rel_block_tx', ['hash:START_ID(Block)', 'txid:END_ID(Transaction)'])
    write_header('rel_tx_output', ['txid:START_ID(Transaction)', 'txid_n:END_ID(Output)'])
    write_header('rel_input', ['txid:END_ID(Transaction)', 'txid_n:START_ID(Output)'])
    write_header('rel_output_address', ['txid_n:START_ID(Output)', 'address:END_ID(Address)'])

    with open(get_path('blocks'), 'a') as blocks_file, \
            open(get_path('transactions'), 'a') as transactions_file, \
            open(get_path('outputs'), 'a') as outputs_file, \
            open(get_path('addresses'), 'a') as addresses_file, \
            open(get_path('rel_block_tx'), 'a') as rel_block_tx_file, \
            open(get_path('rel_tx_output'), 'a') as rel_tx_output_file, \
            open(get_path('rel_input'), 'a') as rel_input_file, \
            open(get_path('rel_output_address'), 'a') as rel_output_address_file:
        block_writer = csv.writer(blocks_file)
        transaction_writer = csv.writer(transactions_file)
        output_writer = csv.writer(outputs_file)
        address_writer = csv.writer(addresses_file)
        rel_block_tx_writer = csv.writer(rel_block_tx_file)
        rel_tx_output_writer = csv.writer(rel_tx_output_file)
        rel_input_writer = csv.writer(rel_input_file)
        rel_output_address_writer = csv.writer(rel_output_address_file)

        block_hash = start_block_hash
        with requests.Session() as session:
            for counter in range(0, number_of_blocks):
                block_hash = get_block(block_hash)

                if progress:
                    last_percentage = (counter * 100) // number_of_blocks
                    percentage = ((counter + 1) * 100) // number_of_blocks
                    if percentage > last_percentage:
                        progress((counter + 1) / number_of_blocks)
