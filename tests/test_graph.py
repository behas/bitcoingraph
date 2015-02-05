import unittest
from tempfile import NamedTemporaryFile

from bitcoingraph.graph import Graph, TransactionGraph
from bitcoingraph.blockchain import BlockChain

from tests.rpc_mock import BitcoinProxyMock


TEST_CSV = 'tests/data/tx_graph.csv'


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

    def test_add_edge(self):
        edge = dict({'txid': 'abc', 'src': '123', 'tgt': '456'})
        self.graph.add_edge(edge)
        self.assertEqual(1, self.graph.count_edges())

    def test_add_count(self):
        edge1 = dict({'txid': 'abc', 'src': '123', 'tgt': '456'})
        self.graph.add_edge(edge1)
        self.assertEqual(1, self.graph.count_edges())
        edge2 = dict({'txid': 'def', 'src': '123', 'tgt': '789'})
        self.graph.add_edge(edge2)
        self.assertEqual(2, self.graph.count_edges())

    def test_list_edges(self):
        edge1 = dict({'txid': 'ghi', 'src': '789', 'tgt': '101'})
        self.graph.add_edge(edge1)
        edge2 = dict({'txid': 'def', 'src': '123', 'tgt': '789'})
        self.graph.add_edge(edge2)
        edge3 = dict({'txid': 'abc', 'src': '123', 'tgt': '456'})
        self.graph.add_edge(edge3)
        edges = [edge for edge in self.graph.list_edges()]
        self.assertIn(edge1, edges)
        self.assertIn(edge2, edges)
        self.assertIn(edge3, edges)

    def test_list_edges_sorted(self):
        edge1 = dict({'txid': 'ghi', 'src': '789', 'tgt': '101'})
        self.graph.add_edge(edge1)
        edge2 = dict({'txid': 'def', 'src': '123', 'tgt': '789'})
        self.graph.add_edge(edge2)
        edge3 = dict({'txid': 'abc', 'src': '123', 'tgt': '456'})
        self.graph.add_edge(edge3)
        edges = [edge for edge in self.graph.list_edges('txid')]
        self.assertEqual(edge3, edges[0])
        self.assertEqual(edge2, edges[1])
        self.assertEqual(edge1, edges[2])


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
        self.txgraph.generate_from_blockchain(99999, 100000)
        self.assertEqual(7, self.txgraph.count_edges())

    def test_export_to_csv(self):
        tempfile = NamedTemporaryFile(mode='w+')
        self.txgraph.export_to_csv(99999, 100000, tempfile.name)
        with open(tempfile.name) as f:
            content = f.readlines()
            for line in content:
                self.assertIn(line, self.reference_file)

    def test_load_from_file(self):
        self.txgraph.load_from_file(TEST_CSV)
        self.assertEqual(7, self.txgraph.count_edges())


class TestEntityGraph(unittest.TestCase):

    def test_generate_from_tx_graph(self):
        pass

    def test_generate_from_file(self):
        pass
