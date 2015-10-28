"""
bitcoingraph

A Python library for extracting and navigating graph structures from
the Bitcoin block chain.

"""

import csv
import logging
import os

from bitcoingraph.blockchain import Blockchain, BlockchainException
from bitcoingraph.graph_controller import GraphController
from bitcoingraph.rpc import BitcoinProxy, JSONRPCException

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


def get_graph_db(host, port, user, password):
    return GraphController(host, port, user, password)
