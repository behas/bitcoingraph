"""
bitcoingraph

A Python library for extracting and navigating graph structures from
the Bitcoin block chain.

"""

__author__ = 'Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)'
__copyright__ = 'Copyright 2015, Bernhard Haslhofer'
__license__ = "MIT"
__version__ = '0.1'

import csv

from bitcoingraph.blockchain import BlockchainException

__all__ = ['generate_tx_graph']


def generate_tx_graph(blockchain, start_block, end_block,
                      output_file, callback=None):
    """
    Generates transaction graph from the block chain and saves it to a
    CSV file.

    :param BlockChain blockchain: instantiated blockchain object
    :param int start_block: start block of transaction generation range
    :param int end_block: end block of transaction genration range
    """
    cvs_writer = csv.writer(output_file, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    cvs_writer.writerow(['txid', 'src_addr', 'tgt_addr', 'value',
                         'timestamp', 'block_height'])
    for block in blockchain.get_blocks_in_range(start_block, end_block):
        progress = block.height / (end_block - start_block)
        if callback:
            callback(progress)
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
