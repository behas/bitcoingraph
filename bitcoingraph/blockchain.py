#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Copyright 2014 Bernhard Haslhofer

    A collection of block chain handling wrapers

"""


import json
import datetime as dt

from bitcoingraph.rpc import JSONRPCException


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

    def __init__(self, raw_data, blockchain):
        self._raw_data = raw_data
        self._blockchain = blockchain

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

    def __init__(self, raw_data, blockchain):
        super().__init__(raw_data, blockchain)

    @property
    def height(self):
        return int(self._raw_data['height'])

    @property
    def hash(self):
        return self._raw_data['hash']

    @property
    def nextblockhash(self):
        return self._raw_data['nextblockhash']

    @property
    def hasnextblock(self):
        return 'nextblockhash' in self._raw_data

    @property
    def nextblock(self):
        if self.hasnextblock:
            block_hash = self.nextblockhash
            return self._blockchain.get_block_by_hash(block_hash)
        else:
            return None

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

    def __init__(self, raw_data, blockchain):
        super().__init__(raw_data, blockchain)

    @property
    def blocktime(self):
        return to_time(self._raw_data['blocktime'])

    @property
    def id(self):
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


class BlockchainException(Exception):
    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return repr(self.msg)


class BlockChain:

    """
    A handler for accessing Bitcoin blockchain data objects.
    """

    def __init__(self, bitcoin_proxy):
        self._bitcoin_proxy = bitcoin_proxy

    def get_block_by_hash(self, block_hash):
        # Returns block by hash
        try:
            raw_block_data = self._bitcoin_proxy.getblock(block_hash)
            return Block(raw_block_data, self)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve block %s"
                                      % (block_hash), exc)

    def get_block_by_height(self, block_height):
        # Returns block by height
        try:
            block_hash = self._bitcoin_proxy.getblockhash(block_height)
            return self.get_block_by_hash(block_hash)
        except JSONRPCException as exc:
            print("Raising Exceptions")
            raise BlockchainException("Cannot retrieve block with height %s"
                                      % (block_height), exc)

    def get_block_range(self, start_height=0, end_height=0):
        # Returns blocks for a given height range
        block = self.get_block_by_height(start_height)
        while (block.height <= end_height):
            yield block
            if not block.hasnextblock:
                break
            else:
                block = block.nextblock

    def get_transaction(self, tx_id):
        # Returns transaction for a given transaction hash
        try:
            raw_tx_data = self._bitcoin_proxy.getrawtransaction(tx_id)
            return Transaction(raw_tx_data, self)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve transaction with id %s"
                                      % (tx_id), exc)
