#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Copyright 2014 Bernhard Haslhofer

    Generates transaction graph from Bitcoin blockchain

"""


import rpc
import json


def print_json(obj):
    print(json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')))


# TODO: write TransactionGenerator class with transaction generator function

DEFAULT_SERVICE_URI = 'http://bitcoinrpc:pass@localhost:8332/'


class TransactionGraphHandler(object):
    """
    Handler for Bitcoin transaction graph.
    """

    def __init__(self, bitcoin_service_uri=None):
        # initialize Bitcoin proxy
        if bitcoin_service_uri is not None:
            self.bcProxy = rpc.BitcoinProxy(bitcoin_service_uri)
        else:
            self.bcProxy = rpc.BitcoinProxy(DEFAULT_SERVICE_URI)

    def transaction_range(self, first_height=0, last_height=0):
        if first_height == 0:
            first_height = 0
        if last_height is None:
            last_height = self.bcProxy.getblockcount()

        current_height = first_height
        next_block_hash = self.bcProxy.getblockhash(first_height)

        while (next_block_hash is not None) and \
              (current_height <= last_height):

            block = self.bcProxy.getblock(next_block_hash)
            for tx in block['tx']:
                transaction = self.bcProxy.getrawtransaction(tx)
                yield transaction
            if 'nextblockhash' in block:
                next_block_hash = block['nextblockhash']
            else:
                next_block_hash = None
            current_height += 1


if __name__ == '__main__':
    handler = TransactionGraphHandler()
    transactions = handler.transaction_range(100000, 100000)
    for tx in transactions:
        # print("Bla")
        print_json(tx)
