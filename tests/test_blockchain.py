import unittest

from tests.rpc_mock import BitcoinProxyMock

from bitcoingraph.blockchain import BlockChain

BH1 = "000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506"
BH1_HEIGHT = 100000

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.bitcoin_proxy = BitcoinProxyMock()
        self.blockchain = BlockChain(self.bitcoin_proxy)

    def test_init(self):
        self.assertIsNotNone(self.blockchain)

    ## Test Blockchain accessors

    def test_get_block_by_hash(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.hash, BH1)

    def test_get_block_by_height(self):
        block = self.blockchain.get_block_by_height(BH1_HEIGHT)
        self.assertEqual(block.height, BH1_HEIGHT)

    def test_get_block_range(self):
        blocks = [block for block in self.blockchain.get_block_range(
                  99999, 100001)]
        self.assertEqual(len(blocks), 3)
        self.assertEquals(blocks[0].height, 99999)
        self.assertEquals(blocks[1].height, 100000)
        self.assertEquals(blocks[2].height, 100001)

