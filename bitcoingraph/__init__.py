__all__ = ['generate_tx_graph']

__version__ = '0.1dev'

import csv

from bitcoingraph.blockchain import BlockchainException


def generate_tx_graph(blockchain, start_block, end_block, output_file):
    cvs_writer = csv.writer(output_file, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    cvs_writer.writerow(['txid', 'src_addr', 'tgt_addr', 'value',
                         'timestamp', 'block_height'])
    for block in blockchain.get_blocks_in_range(start_block, end_block):
        for tx in block.transactions:
            try:
                txid = tx.id
                timestamp = tx.time
                for bc_flow in tx.bc_flows:
                    src_addr = bc_flow['src']
                    if src_addr is None:
                        src_addr = "NULL"
                    tgt_addr = bc_flow['tgt']
                    if tgt_addr is None:
                        tgt_addr = "NULL"
                    value = bc_flow['value']
                    block_height = block.height
                    cvs_writer.writerow([txid, src_addr, tgt_addr,
                                         value, timestamp, block_height])
            except BlockchainException as exc:
                print(exc)
