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

from bitcoingraph.blockchain import BlockChain
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


# Blockchain interfaces

def create_blockchain(service_uri):
    """
    Creates a blockchain object for a given Bitcoin Core JSON-RPC Service.
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


# Transaction graph interfaces

def export_tx_graph(service_uri, start_block, end_block,
                    output_file, progress=None):
    """
    Generates transaction graph from the Blockchain and exports it to a
    CSV file.

    :param BlockChain blockchain: instantiated blockchain object
    :param int start_block: start block of transaction export range
    :param int end_block: end block of transaction export range
    """
    blockchain = create_blockchain(service_uri)
    tx_graph = TransactionGraph(blockchain)
    tx_graph.export_to_csv(start_block, end_block, output_file, progress)


def load_tx_graph_from_file(tx_graph_file):
    """
    Loads transaction graph from given CSV file.
    """
    tx_graph = TransactionGraph()
    tx_graph.load_from_file(tx_graph_file)
    return tx_graph


# Entity graph interfaces

def export_et_graph(tx_graph_file, output_dir):
    """
    Export entity graph from transaction graph.
    """
    et_graph = EntityGraph()
    et_graph.generate_from_tx_data(tx_graph_file=tx_graph_file)
    et_graph.export_to_csv(output_dir)


def load_et_graph_from_directory(et_graph_directory):
    """
    Loads entity graph and mapping info from directory containing CSV files.
    """
    et_graph = EntityGraph()
    et_graph.load_from_dir(et_graph_directory)
    return et_graph
