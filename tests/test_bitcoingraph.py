import unittest
from tempfile import TemporaryFile

import bitcoingraph as bgraph
from bitcoingraph.graph import TransactionGraph

from tests.rpc_mock import BitcoinProxyMock


class TestBitcoinGraph(unittest.TestCase):

    def setUp(self):
        self.bitcoin_proxy = BitcoinProxyMock()

    def test_dump_tx_graph(self):
        tx_graph = TransactionGraph(self.bitcoin_proxy)
        with TemporaryFile(mode='w+') as csv_file:
            bgraph.dump(tx_graph, csv_file)
