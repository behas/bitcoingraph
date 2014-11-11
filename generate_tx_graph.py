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

    current_block = first_block
    next_block_hash = bcProxy.getblockhash(first_block)

    while (next_block_hash is not None) and (current_block <= last_block):
        block = bcProxy.getblock(next_block_hash)
        print_json(block)
        if 'nextblockhash' in block:
            next_block_hash = block['nextblockhash']
        else:
            next_block_hash = None
        current_block += 1

if __name__ == '__main__':
    generate_tx_graph(106, 106)
