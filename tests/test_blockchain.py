import unittest

from tests.rpc_mock import BitcoinProxyMock

from bitcoingraph.blockchain import *

BH1 = "000000000002d01c1fccc21636b607dfd930d31d01c3a62104612a1719011250"
BH1_HEIGHT = 99999
BH2 = "000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506"
BH2_HEIGHT = 100000
BH3 = "00000000000080b66c911bd5ba14a74260057311eaeb1982802f7010f1a9f090"
BH3_HEIGHT = 100001

# standard transactions
TX1 = "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87"
TX2 = "fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4"
TX3 = "87a157f3fd88ac7907c05fc55e271dc4acdc5605d187d646604ca8c0e9382e03"

# transaction with unknown output
TXE = "a288fec5559c3f73fd3d93db8e8460562ebfe2fcf04a5114e8d0f2920a6270dc"

# transaction with multiple in and outputs
TXM = "d5f013abf2cf4af6d68bcacd675c91f19bab5b7103b4ac2f4941686eb47da1f0"


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

    def test_transactions(self):
        block = self.blockchain.get_block_by_hash(BH1)
        txs = [tx for tx in block.transactions]
        self.assertEqual(len(txs), 1)
        for tx in txs:
            self.assertIsNotNone(tx.id)
        block = self.blockchain.get_block_by_hash(BH2)
        txs = [tx for tx in block.transactions]
        self.assertEqual(len(txs), 4)
        for tx in txs:
            self.assertIsNotNone(tx.id)


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

    def test_tx_output_index(self):
        tx = self.blockchain.get_transaction(TX2)
        tx_input = tx.inputs[0]
        self.assertEqual(tx_input.prev_tx_output_index, 0)

    def test_tx_output_index_coinbase(self):
        tx = self.blockchain.get_transaction(TX1)
        tx_input = tx.inputs[0]
        self.assertIsNone(tx_input.prev_tx_output_index)

    def test_prev_tx_output(self):
        tx = self.blockchain.get_transaction(TX2)
        tx_input = tx.inputs[0]
        prev_tx_output = tx_input.prev_tx_output
        self.assertIsNotNone(prev_tx_output)

    def test_addresses(self):
        tx = self.blockchain.get_transaction(TX2)
        self.assertEqual("1BNwxHGaFbeUBitpjy2AsKpJ29Ybxntqvb",
                         tx.inputs[0].addresses[0])


class TestTxOutput(TestBlockchainObject):

    def test_index(self):
        tx = self.blockchain.get_transaction(TX2)
        self.assertEqual(0, tx.outputs[0].index)
        self.assertEqual(1, tx.outputs[1].index)

    def test_value(self):
        tx = self.blockchain.get_transaction(TX2)
        self.assertEqual(5.56000000, tx.outputs[0].value)
        self.assertEqual(44.44000000, tx.outputs[1].value)

    def test_addresses(self):
        tx = self.blockchain.get_transaction(TX2)
        self.assertEqual("1JqDybm2nWTENrHvMyafbSXXtTk5Uv5QAn",
                         tx.outputs[0].addresses[0])
        self.assertEqual("1EYTGtG4LnFfiMvjJdsU7GMGCQvsRSjYhx",
                         tx.outputs[1].addresses[0])

    def test_empty_addresses(self):
        tx = self.blockchain.get_transaction(TXE)
        self.assertEqual("152hHAq6kHoLw2FCT8G37uLEts6oFVjZKt",
                         tx.outputs[0].addresses[0])
        self.assertIsNone(tx.outputs[1].addresses)


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

    def test_is_coinbase_tx(self):
        self.assertTrue(self.blockchain.get_transaction(TX1).is_coinbase_tx)
        self.assertFalse(self.blockchain.get_transaction(TX2).is_coinbase_tx)

    def test_vout_count(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertEqual(tx.vout_count, 1)
        tx = self.blockchain.get_transaction(TX2)
        self.assertEqual(tx.vout_count, 2)

    def test_outputs(self):
        tx = self.blockchain.get_transaction(TX1)
        self.assertIsInstance(tx.outputs[0], TxOutput)

    def test_bc_flows(self):
        tx = self.blockchain.get_transaction(TX2)
        f1 = {'src': '1BNwxHGaFbeUBitpjy2AsKpJ29Ybxntqvb',
              'tgt': '1JqDybm2nWTENrHvMyafbSXXtTk5Uv5QAn',
              'value': 5.56000000}
        f2 = {'src': '1BNwxHGaFbeUBitpjy2AsKpJ29Ybxntqvb',
              'tgt': '1EYTGtG4LnFfiMvjJdsU7GMGCQvsRSjYhx',
              'value': 44.44000000}
        self.assertTrue(f1 in tx.bc_flows)
        self.assertTrue(f2 in tx.bc_flows)

    def test_bc_flows_coinbase(self):
        tx = self.blockchain.get_transaction(TX1)
        f1 = {'src': None,
              'tgt': '1HWqMzw1jfpXb3xyuUZ4uWXY4tqL2cW47J',
              'value': 50.00000000}
        self.assertTrue(f1 in tx.bc_flows)

    def test_bc_flows_multiple_inputs(self):
        tcx = self.blockchain.get_transaction(TXM)
        f1 = {'src': '1Nj6ssafuCe8JqDaR1n3Jw61gZ9FXJim5x',
              'tgt': '1BWwKwTM6phe45zwUVGQq6WipmWZsVbK8h',
              'value': 1.05000000}
        self.assertTrue(f1 in tcx.bc_flows)
        f2 = {'src': '1LjzLspWYZHgBECKvrMKDY5myM2kkCrtKu',
              'tgt': '1BWwKwTM6phe45zwUVGQq6WipmWZsVbK8h',
              'value': 1.05000000}
        self.assertTrue(f2 in tcx.bc_flows)


class TestBlockchain(TestBlockchainObject):

    def test_get_block_by_hash(self):
        block = self.blockchain.get_block_by_hash(BH1)
        self.assertEqual(block.hash, BH1)

    def test_get_block_by_height(self):
        block = self.blockchain.get_block_by_height(BH1_HEIGHT)
        self.assertEqual(block.height, BH1_HEIGHT)

    def test_get_blocks_in_range(self):
        blocks = [block for block in self.blockchain.get_blocks_in_range(
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
