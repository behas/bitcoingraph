"""
bitcoingraph

A Python library for extracting and navigating graph structures from
the Bitcoin block chain.

"""

import csv
import logging
import os

from bitcoingraph.blockchain import Blockchain, BlockchainException
from bitcoingraph.rpc import BitcoinProxy, JSONRPCException


__author__ = 'Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)'
__copyright__ = 'Copyright 2015, Bernhard Haslhofer'
__license__ = "MIT"
__version__ = '0.3dev'

__all__ = ['conncect_blockchain', 'export_transactions']

logger = logging.getLogger('bitcoingraph')


class BitcoingraphException(Exception):
    """
    Top-level exception raised when interacting with bitcoingraph library.
    """

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return self.msg


# Blockchain interfaces

def get_blockchain(service_uri):
    """
    Connects to Bitcoin Core (via JSON-RPC) and returns a Blockchain object.
    """
    try:
        logger.debug("Connecting to Bitcoin Core at {}".format(service_uri))
        bc_proxy = BitcoinProxy(service_uri)
        bc_proxy.getinfo()
        logger.debug("Connection successful.")
        blockchain = Blockchain(bc_proxy)
        return blockchain
    except JSONRPCException as exc:
        raise BitcoingraphException("Couldn't connect to {}.".format(
                                        service_uri), exc)


def export_transactions(blockchain, start_block, end_block, neo4j=False,
                        output_path=None, progress=None):
    """
    Exports transactions in a given block range to CSV file.
    """
    if start_block is None:
        start_block = 1
    if end_block is None:
        end_block = blockchain.get_max_blockheight()

    if output_path is None:
        output_path = 'tx_{}_{}'.format(start_block, end_block)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    tx_file = output_path + "/" + "transactions.csv"
    tx_address_file = output_path + "/" + "addresses.csv"
    tx_input_file = output_path + "/" + "inputs.csv"
    tx_output_file = output_path + "/" + "outputs.csv"

    if neo4j:
        fn_tx_file = ['txid:ID(Transaction)', 'block', 'timestamp', 'total']
        fn_address_file = ['address:ID(Address)']
        fn_in_file = [':START_ID(Address)', ':END_ID(Transaction)', 'value']
        fn_out_file = [':START_ID(Transaction)', ':END_ID(Address)', 'value']
    else:
        fn_tx_file = ['txid', 'block', 'timestamp', 'total']
        fn_address_file = ['address']
        fn_in_file = ['address', 'txid', 'value']
        fn_out_file = ['txid', 'address', 'value']

    with open(tx_file, 'w') as tx_csv_file, \
            open(tx_address_file, 'w') as address_csv_file, \
            open(tx_input_file, 'w') as input_csv_file, \
            open(tx_output_file, 'w') as output_csv_file:

        tx_writer = csv.writer(tx_csv_file)
        addr_writer = csv.writer(address_csv_file)
        input_writer = csv.writer(input_csv_file)
        output_writer = csv.writer(output_csv_file)

        tx_writer.writerow(fn_tx_file)
        addr_writer.writerow(fn_address_file)
        input_writer.writerow(fn_in_file)
        output_writer.writerow(fn_out_file)

        try:
            for idx, block in enumerate(blockchain.get_blocks_in_range(
                                        start_block, end_block)):
                # transactions
                for tx in block.transactions:
                    tx_writer.writerow([tx.id, block.height,
                                        tx.time, tx.flow_sum])
                # inputs
                if tx.is_coinbase_tx:
                    input_writer.writerow(['COINBASE', tx.id, tx.flow_sum])
                    addr_writer.writerow(['COINBASE'])
                else:
                    for tx_input in tx.get_inputs():
                        referenced_output = tx_input.prev_tx_output
                        input_writer.writerow([referenced_output.address,
                                               tx.id,
                                               referenced_output.value])
                        addr_writer.writerow([referenced_output.address])
                # outputs
                for tx_output in tx.get_outputs():
                    if tx_output.address is not None:
                        output_writer.writerow([tx.id,
                                                tx_output.address,
                                                tx_output.value])
                        addr_writer.writerow([tx_output.address])
                if progress:
                    block_range = end_block - start_block
                    if block_range == 0:
                        block_range = 1
                    progress(idx / block_range)
        except BlockchainException as exc:
            raise BitcoingraphException("Transaction export failed", exc)
