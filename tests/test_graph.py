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

    def test_generate_from_blockchain(self):
        edges = [edge for edge in
                 self.txgraph._generate_from_blockchain(99999, 100000)]
        self.assertEqual(7, len(edges))

    def test_export_to_csv(self):
        tempfile = NamedTemporaryFile(mode='w+')
        self.txgraph.export_to_csv(99999, 100000, tempfile.name)
        with open(tempfile.name) as f:
            content = f.readlines()
            for line in content:
                self.assertIn(line, self.reference_file)

    def test_load_from_blockchain(self):
        self.txgraph.load(99999, 100000)
        self.assertEqual(7, self.txgraph.count_edges())

    def test_load_from_file(self):
        self.txgraph.load(99999, 100000, TEST_CSV)
        self.assertEqual(7, self.txgraph.count_edges())
