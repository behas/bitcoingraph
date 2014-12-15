import unittest

from tests.rpc_mock import BitcoinProxyMock

from bitcoingraph.blockchain import BlockChain, BlockchainException, TxInput

BH1 = "000000000002d01c1fccc21636b607dfd930d31d01c3a62104612a1719011250"
BH1_HEIGHT = 99999
BH2 = "000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506"
BH2_HEIGHT = 100000
BH3 = "00000000000080b66c911bd5ba14a74260057311eaeb1982802f7010f1a9f090"
BH3_HEIGHT = 100001

TX1 = "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87"
TX2 = "fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4"
TX3 = "87a157f3fd88ac7907c05fc55e271dc4acdc5605d187d646604ca8c0e9382e03"


class TestBlockchainObject(unittest.TestCase):

    def setUp(self):
        self.bitcoin_proxy = BitcoinProxyMock()
        self.blockchain = BlockChain(self.bitcoin_proxy)

    def test_init(self):
        self.assertIsNotNone(self.blockchain)
        self.assertIsNotNone(self.bitcoin_proxy)


class TestBlock(TestBlockchainObject):

    def test_time(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.time, 1293623731)

    def test_time_as_dt(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.time_as_dt, "2010-12-29 11:55:31")

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

    def hasnextblock(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertTrue(block.hasnextblock)
        block = self.blockchain.get_block_by_hash(BH3)
        self.assertFalse(block.hasnextblock)

    def test_nextblock(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.nextblock.height, BH2_HEIGHT)
        block = self.blockchain.get_block_by_hash(BH3)
        self.assertIsNone(block.nextblock)

    def test_tx_count(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.tx_count, 1)
        block = self.blockchain.get_block_by_hash(BH2)
        self.assertEqual(block.tx_count, 4)

    def test_tx_ids(self):
        block = self.blockchain.get_block_by_hash(BH2)
        self.assertTrue(TX1 in block.tx_ids)


class TestTxInput(TestBlockchainObject):

    def test_is_coinbase(self):
        tx = self.blockchain.get_transaction(TX1)
        tx_input = tx.inputs[0]
        self.assertTrue(tx_input.is_coinbase)

    def test_is_not_coinbase(self):
        tx = self.blockchain.get_transaction(TX2)
        tx_input = tx.inputs[0]
        self.assertFalse(tx_input.is_coinbase)

    def test_prev_tx_hash(self):
        tx = self.blockchain.get_transaction(TX2)
        tx_input = tx.inputs[0]
        self.assertEqual(tx_input.prev_tx_hash, TX3)

    def test_prev_tx_coinbase(self):
        tx = self.blockchain.get_transaction(TX1)
        tx_input = tx.inputs[0]
        self.assertIsNone(tx_input.prev_tx_hash)

    def test_tx_out_index(self):
        tx = self.blockchain.get_transaction(TX2)
        tx_input = tx.inputs[0]
        self.assertEqual(tx_input.prev_tx_out_index, 0)

    def test_tx_out_index_coinbase(self):
        tx = self.blockchain.get_transaction(TX1)
        tx_input = tx.inputs[0]
        self.assertIsNone(tx_input.prev_tx_out_index)


class TestTransaction(TestBlockchainObject):

    def test_time(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.time, 1293623863)

    def test_time_as_dt(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.time_as_dt, "2010-12-29 11:57:43")

    def test_blocktime(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.blocktime, 1293623863)

    def test_id(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.id, TX1)

    def test_vin_count(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.vin_count, 1)
        tx = self.blockchain.get_transaction(TX2)
        self.assertEqual(tx.vin_count, 1)

    def test_inputs(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertIsInstance(tx.inputs[0], TxInput)

    def test_vout_count(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.vout_count, 1)
        tx = self.blockchain.get_transaction(TX2)
        self.assertEqual(tx.vout_count, 2)


class TestBlockchain(TestBlockchainObject):

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

    def test_exceptions(self):
        with self.assertRaises(BlockchainException) as cm:
            self.blockchain.get_block_by_hash("aa")
        self.assertEqual("Cannot retrieve block aa", cm.exception.msg)

        with self.assertRaises(BlockchainException) as cm:
            self.blockchain.get_block_by_height(123)
        self.assertEqual("Cannot retrieve block with height 123",
                         cm.exception.msg)

        with self.assertRaises(BlockchainException) as cm:
            self.blockchain.get_transaction("bb")
        self.assertEqual("Cannot retrieve transaction with id bb",
                         cm.exception.msg)
