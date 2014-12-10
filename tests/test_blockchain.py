import unittest

from tests.rpc_mock import BitcoinProxyMock

from bitcoingraph.blockchain import BlockChain


class TestBlockchain(unittest.TestCase):

    def setUp(self):
        bitcoin_proxy = BitcoinProxyMock()
        self.blockchain = BlockChain(bitcoin_proxy)

    def test_init(self):
        self.assertIsNotNone(self.blockchain)
