import unittest
from tempfile import NamedTemporaryFile

from bitcoingraph.graph import TransactionGraph
from bitcoingraph.blockchain import BlockChain

from tests.rpc_mock import BitcoinProxyMock


TEST_CSV = 'tests/data/tx_graph.csv'


class TestTransactionGraph(unittest.TestCase):

    def setUp(self):
        self.bitcoin_proxy = BitcoinProxyMock()
        self.blockchain = BlockChain(self.bitcoin_proxy)
        self.txgraph = TransactionGraph(self.blockchain)
        self.reference_file = self.load_reference_file()

    def load_reference_file(self):
        reference_file = None
        with open(TEST_CSV, 'r') as f:
            reference_file = f.readlines()
        return reference_file

    def test_generate(self):
        edges = [edge for edge in self.txgraph.generate_edges(99999, 100000)]
        self.assertEqual(7, len(edges))

    def test_export_to_csv(self):
        with NamedTemporaryFile(mode='w+') as csv_file:
            self.txgraph.export_to_csv(99999, 100000, csv_file)
            csv_file.flush()
            with open(csv_file.name) as f:
                content = f.readlines()
                for line in content:
                    self.assertIn(line, self.reference_file)
