from bitcoingraph.bitcoind import BitcoinProxy, JSONRPCException

from pathlib import Path

import json


TEST_DATA_PATH = "tests/data"


class BitcoinProxyMock(BitcoinProxy):

    def __init__(self, host=None, port=None):
        super().__init__(host, port)
        self.heights = {}
        self.blocks = {}
        self.txs = {}
        self.load_testdata()

    # Load test data into local dicts
    def load_testdata(self):
        p = Path(TEST_DATA_PATH)
        files = [x for x in p.iterdir()
                 if x.is_file() and x.name.endswith('json')]
        for f in files:
            if f.name.startswith("block"):
                height = f.name[6:-5]
                with f.open() as jf:
                    raw_block = json.load(jf)
                    block_hash = raw_block['hash']
                    self.heights[int(height)] = block_hash
                    self.blocks[block_hash] = raw_block
            elif f.name.startswith("tx"):
                tx_hash = f.name[3:-5]
                with f.open() as jf:
                    raw_block = json.load(jf)
                    self.txs[tx_hash] = raw_block

    # Override production proxy methods

    def getblock(self, block_hash):
        if block_hash not in self.blocks:
            raise JSONRPCException("Unknown block", block_hash)
        else:
            return self.blocks[block_hash]

    def getblockcount(self):
        return max(self.heights.keys())

    def getblockhash(self, block_height):
        if block_height not in self.heights:
            raise JSONRPCException("Unknown height", block_height)
        else:
            return self.heights[block_height]

    def getinfo(self):
        print("No info")

    def getrawtransaction(self, tx_id, verbose=1):
        if tx_id not in self.txs:
            raise JSONRPCException("Unknown transaction", tx_id)
        else:
            return self.txs[tx_id]

    def getrawtransactions(self, tx_ids, verbose=1):
        results = []
        for tx_id in tx_ids:
            results.append(self.getrawtransaction(tx_id, verbose))
        return results
