import unittest

from tests.rpc_mock import BitcoinProxyMock

from bitcoingraph.blockchain import BlockChain

BH1 = "000000000002d01c1fccc21636b607dfd930d31d01c3a62104612a1719011250"
BH1_HEIGHT = 99999
BH2 = "000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506"
BH2_HEIGHT = 100000
BH3 = "00000000000080b66c911bd5ba14a74260057311eaeb1982802f7010f1a9f090"
BH3_HEIGHT = 100001

TX1 = "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87"


class TestBlock(unittest.TestCase):

    def setUp(self):
        self.bitcoin_proxy = BitcoinProxyMock()
        self.blockchain = BlockChain(self.bitcoin_proxy)

    def test_height(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.height, BH1_HEIGHT)

    def test_hash(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.hash, BH1)

    def test_nextblockhash(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertTrue(block.hasnextblock)
        block = self.blockchain.get_block_by_hash(BH3)
        self.assertFalse(block.hasnextblock)

    def test_nextblock(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.nextblock.height, BH2_HEIGHT)


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
        self.assertEqual(blocks[0].height, 99999)
        self.assertEqual(blocks[1].height, 100000)
        self.assertEqual(blocks[2].height, 100001)

    def test_get_transaction(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.id, TX1)
