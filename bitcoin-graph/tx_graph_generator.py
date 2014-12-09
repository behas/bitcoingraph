#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Copyright 2014 Bernhard Haslhofer

    Generates transaction graph from Bitcoin blockchain

"""


import rpc
import json

import datetime as dt


DEFAULT_SERVICE_URI = 'http://bitcoinrpc:pass@localhost:8332/'


def to_json(raw_data):
    return json.dumps(raw_data, sort_keys=True,
                      indent=4, separators=(',', ': '))


def to_time(numeric_string):
    return dt.datetime.fromtimestamp(
        int(numeric_string)).strftime('%Y-%m-%d %H:%M:%S')


class BlockchainObject:
    """
    Generic wrapper class for any kind of Blockchain BlockchainObject
    """
    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def time(self):
        return to_time(self._raw_data['time'])

    def __str__(self):
        return to_json(self._raw_data)

    def __repr__(self):
        return to_json(self._raw_data)


class Block(BlockchainObject):
    """
    Wrapper class for block chain data
    """
    def __init__(self, raw_data):
        super().__init__(raw_data)

    @property
    def height(self):
        return int(self._raw_data['height'])

    @property
    def tx_count(self):
        return len(self._raw_data['tx'])

    @property
    def tx_ids(self):
        return self._raw_data['tx']


class Transaction(BlockchainObject):
    """
    Wrapper class for bitcoin transactions
    """
    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def blocktime(self):
        return to_time(self._raw_data['blocktime'])

    @property
    def txid(self):
        return self._raw_data['txid']

    @property
    def vin_count(self):
        if 'vin' in self._raw_data:
            return len(self._raw_data['vin'])
        else:
            return 0

    @property
    def vout_count(self):
        if 'vout' in self._raw_data:
            return len(self._raw_data['vout'])
        else:
            return 0


class BlockChainHandler:
    """
    A handler for the Bitcoin blockchain.
    """

    def __init__(self, bitcoin_service_uri=None):
        # initialize Bitcoin proxy
        if bitcoin_service_uri is not None:
            self._bcProxy = rpc.BitcoinProxy(bitcoin_service_uri)
        else:
            self._bcProxy = rpc.BitcoinProxy(DEFAULT_SERVICE_URI)

    def blocks(self, first_height=0, last_height=0):
        # Generator yielding block json data for a given block range
        if first_height == 0:
            first_height = 0
        if last_height is None:
            last_height = self._bcProxy.getblockcount()

        current_height = first_height
        next_block_hash = self._bcProxy.getblockhash(first_height)

        while (next_block_hash is not None) and \
              (current_height <= last_height):

            raw_block_data = self._bcProxy.getblock(next_block_hash)
            yield Block(raw_block_data)
            if 'nextblockhash' in raw_block_data:
                next_block_hash = raw_block_data['nextblockhash']
            else:
                next_block_hash = None
            current_height += 1

    def transactions(self, tx_ids):
        # Generator yielding transaction json data for a given tx_id list
        for tx_id in tx_ids:
            raw_tx_data = self._bcProxy.getrawtransaction(tx_id)
            yield Transaction(raw_tx_data)

if __name__ == '__main__':
    handler = BlockChainHandler()
    for block in handler.blocks(105, 105):
        print(block.height, block.time, block.tx_count)
        for transaction in handler.transactions(block.tx_ids):
            print(transaction)
