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


def generate_tx_graph(first_block=0, last_block=None):
    bcProxy = rpc.BitcoinProxy('http://bitcoinrpc:pass@localhost:8332/')
    if first_block == 0:
        first_block = 0
    if last_block is None:
        last_block = bcProxy.getblockcount()

    print("Generating transaction graph from block %d to %d..." % (first_block,
          last_block))

    for x in range(first_block, last_block + 1):
        block_hash = bcProxy.getblockhash(first_block)
        block = bcProxy.getblock(block_hash)
        print_json(block)

if __name__ == '__main__':
    generate_tx_graph(105,106)
