import unittest
from tempfile import NamedTemporaryFile

import bitcoingraph as bgraph
from bitcoingraph.blockchain import BlockChain

from tests.rpc_mock import BitcoinProxyMock


TEST_CSV = 'tests/data/tx_graph.csv'


class TestBitcoinGraph(unittest.TestCase):

    def setUp(self):
        self.bitcoin_proxy = BitcoinProxyMock()
        self.blockchain = BlockChain(self.bitcoin_proxy)

    def test_generate_tx_graph(self):
        reference_file = None
        with open(TEST_CSV, 'r') as f:
            reference_file = f.readlines()
        with NamedTemporaryFile(mode='w+') as csv_file:
            bgraph.generate_tx_graph(self.blockchain, 99999, 100000, csv_file)
            csv_file.flush()
            with open(csv_file.name) as f:
                content = f.readlines()
                for line in content:
                    self.assertIn(line, reference_file)
