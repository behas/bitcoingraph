"""
Bitcoin Core JSON-RPC interface.

"""

__author__ = 'Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)'
__copyright__ = 'Copyright 2015, Bernhard Haslhofer'
__license__ = "MIT"

import requests
import json

import time


class JSONRPCException(Exception):
    """
    Exception raised when accessing Bitcoin Core via JSON-RPCS.
    """
    pass


class JSONRPCProxy(object):
    """
    A generic JSON-RPC interface with keep-alive session reuse.
    """

    def __init__(self, url):
        """
        Creates a generic JSON-RPC interface object.

        :param str url: URL of JSON-RPC endpoint
        :return: JSON-RPC proxy object
        :rtype: JSONRPCProxy
        """
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def _call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params),
                              "jsonrpc": "2.0"})
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.get(self._url, headers=self._headers,
                                             data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise JSONRPCException('Failed to connect for RPC call.')
                hadConnectionFailures = True
                print("Couldn't connect for remote procedure call.",
                      "will sleep for ten seconds and then try again...")
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print("Connected for RPC call after retry.")
                break
        if response.status_code not in (200, 500):
            raise JSONRPCException("RPC connection failure: " +
                                   str(response.status_code) + ' ' +
                                   response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] is not None:
            raise JSONRPCException('Error in RPC call: ' +
                                   str(responseJSON['error']))
        return responseJSON['result']


class BitcoinProxy(JSONRPCProxy):
    """
    Proxy to Bitcoin JSON RPC Service.

    Implements a subset of call list described
    `here <https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_Calls_list>`_
    """

    def __init__(self, url):
        """
        Creates a Bitcoin JSON RPC Service object.

        :param str url: URL of Bitcoin Core JSON-RPC endpoint
        :return: bitcoin proxy object
        :rtype: BitcoinProxy
        """
        super().__init__(url)

    def getblock(self, block_hash):
        """
        Returns information about the block with the given hash.

        :param str block_hash: the block hash
        :return: block as JSON
        :rtype: str
        """
        r = self._call('getblock', block_hash)
        return r

    def getblockcount(self):
        """
        Returns the number of blocks in the longest block chain.

        :return: number of blocks in block chain
        :rtype: int
        """
        r = self._call('getblockcount')
        return int(r)

    def getblockhash(self, height):
        """
        Returns hash of block in best-block-chain at given height.

        :param str height: the block height
        :return: block hash
        :rtype: str
        """
        r = self._call('getblockhash', height)
        return r

    def getinfo(self):
        """
        Returns an object containing various state info.

        :return: JSON string with state info
        :rtype: str
        """
        r = self._call('getinfo')
        return r

    def getrawtransaction(self, tx_id, verbose=1):
        """
        Returns raw transaction representation for given transaction id.

        :param str tx_id: transaction id
        :param int verbose: complete transaction record (0 = false, 1 = true)
        :return: raw transaction data as JSON
        :rtype: str
        """
        r = self._call('getrawtransaction', tx_id, verbose)
        return r
