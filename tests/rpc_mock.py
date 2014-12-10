from bitcoingraph.rpc import BitcoinProxy

from pathlib import Path

import json


TEST_DATA_PATH = "tests/data"


class BitcoinProxyMock(BitcoinProxy):

    def __init__(self, url=None):
        super().__init__(url)
        self.heights = {}
        self.blocks = {}
        self.txs = {}
        self.load_testdata()

    # Load test data into local dicts
    def load_testdata(self):
        p = Path(TEST_DATA_PATH)
        files = [x for x in p.iterdir() if x.is_file()]
        for f in files:
            if f.name.startswith("block"):
                height = f.name[6:-5]
                with f.open() as jf:
                    raw_block = json.load(jf)
                    block_hash = raw_block['hash']
                    self.heights[height] = block_hash
                    self.blocks[block_hash] = raw_block
            elif f.name.startswith("tx"):
                tx_hash = f.name[3:-5]
                with f.open() as jf:
                    raw_block = json.load(jf)
                    self.txs[tx_hash] = raw_block

    # Override production proxy methods

    def getblock(self, block_hash):
        return self.blocks[block_hash]

    def getblockcount(self):
        return len(self.blocks)

    def getblockhash(self, block_height):
        return self.heights[block_height]

    def getinfo(self):
        print("No info")

    def getrawtransaction(self, tx_id, verbose=1):
        return self.txs[tx_id]
