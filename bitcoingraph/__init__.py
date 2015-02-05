"""
bitcoingraph

A Python library for extracting and navigating graph structures from
the Bitcoin block chain.

"""

__author__ = 'Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)'
__copyright__ = 'Copyright 2015, Bernhard Haslhofer'
__license__ = "MIT"
__version__ = '0.1'

__all__ = ['export_tx_graph']

import logging
logger = logging.getLogger('bitcoingraph')

from bitcoingraph.blockchain import BlockChain, BlockchainException
from bitcoingraph.rpc import BitcoinProxy, JSONRPCException
from bitcoingraph.graph import TransactionGraph, EntityGraph


class BitcoingraphException(Exception):
    """
    Top-level exception raised when interacting with bitcoingraph library.
    """

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return self.msg


def create_blockchain_proxy(service_uri):
    """
    Connects to Bitcoin Core JSON-RPC serivce and returns Blockchain
    proxy API.
    """
    try:
        logger.debug("Connecting to Bitcoin Core at {}".format(service_uri))
        bc_proxy = BitcoinProxy(service_uri)
        bc_proxy.getinfo()
        logger.debug("Connection successful.")
        blockchain = BlockChain(bc_proxy)
        return blockchain
    except JSONRPCException as exc:
        raise BitcoingraphException("Couldn't connect to {}.".format(service_uri), exc)


def create_tx_graph(blockchain=None):
    """
    Creates transaction graph view on blockchain.

    Note: load graph before processing: tx_graph.load()
    """
    tx_graph = TransactionGraph(blockchain)
    return tx_graph


def export_tx_graph(blockchain, start_block, end_block,
                    output_file, progress=None):
    """
    Exports transaction graph from the Blockchain and saves it to a
    CSV file.

    :param BlockChain blockchain: instantiated blockchain object
    :param int start_block: start block of transaction export range
    :param int end_block: end block of transaction export range
    """
    tx_graph = TransactionGraph(blockchain)
    tx_graph.export_to_csv(start_block, end_block, output_file, progress)


def export_et_graph(tx_graph, output_dir):
    """
    Export entity graph from transaction graph
    """
    et_graph = EntityGraph(tx_graph)
    et_graph.export_to_csv(output_dir)
