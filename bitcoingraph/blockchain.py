#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Copyright 2014 Bernhard Haslhofer

    A collection of block chain handling wrapers

"""


import json

import datetime as dt


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
    def hash(self):
        return self._raw_data['hash']

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


class BlockChain:

    """
    A handler for accessing Bitcoin blockchain data objects.
    """

    def __init__(self, bitcoin_proxy):
        self._bitcoin_proxy = bitcoin_proxy

    def get_block_by_hash(self, block_hash):
        # Returns block with a given height
        raw_block_data = self._bitcoin_proxy.getblock(block_hash)
        return Block(raw_block_data)

    def blocks(self, first_height=0, last_height=0):
        # Generator yielding block json data for a given block range
        if first_height == 0:
            first_height = 0
        if last_height is None:
            last_height = self._bitcoin_proxy.getblockcount()

        current_height = first_height
        next_block_hash = self._bitcoin_proxy.getblockhash(first_height)

        while (next_block_hash is not None) and \
              (current_height <= last_height):

            raw_block_data = self._bitcoin_proxy.getblock(next_block_hash)
            yield Block(raw_block_data)
            if 'nextblockhash' in raw_block_data:
                next_block_hash = raw_block_data['nextblockhash']
            else:
                next_block_hash = None
            current_height += 1

    def transactions(self, tx_ids):
        # Generator yielding transaction json data for a given tx_id list
        for tx_id in tx_ids:
            raw_tx_data = self._bitcoin_proxy.getrawtransaction(tx_id)
            yield Transaction(raw_tx_data)
