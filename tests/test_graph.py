import unittest
from tempfile import NamedTemporaryFile

from bitcoingraph.graph import * 
from bitcoingraph.blockchain import BlockChain

from tests.rpc_mock import BitcoinProxyMock


TEST_CSV = 'tests/data/tx_graph.csv'


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

    def test_add_edge(self):
        edge = { DST: '456', EDGE: '111'}
        self.graph.add_edge("123", edge)
        self.assertEqual(1, self.graph.count_edges())

    def test_add_count(self):
        edge1 = {DST: '456', EDGE: '222'}
        self.graph.add_edge("123", edge1)
        self.assertEqual(1, self.graph.count_edges())
        edge2 = {DST: '789', EDGE: '333'}
        self.graph.add_edge("123", edge2)
        self.assertEqual(2, self.graph.count_edges())

    def test_list_edges(self):
        edge1 = {DST: '101', EDGE: '444'}
        self.graph.add_edge("789", edge1)
        edge2 = {DST: '789', EDGE: '555'}
        self.graph.add_edge("123", edge2)
        edge3 = {DST: '456', EDGE: '666'}
        self.graph.add_edge("123", edge3)
        edges = [edge for edge in self.graph.list_edges()]
        self.assertIn(edge1, edges)
        self.assertIn(edge2, edges)
        self.assertIn(edge3, edges)

    def test_find_edges(self):
        self.assertEqual(0, self.graph.count_edges())
        
        edge1 = {DST: '101', EDGE: '111'}
        self.graph.add_edge("789", edge1)
        edge2 = {DST: '789', EDGE: '222'}
        self.graph.add_edge("123", edge2)
        edge3 = {DST: '456', EDGE: '333'}
        self.graph.add_edge("123", edge3)
        edge4 = {DST: '123', EDGE: '444'}
        self.graph.add_edge("aaa", edge4)
        
        edges = self.graph.find_edges("123")
        self.assertIn(edge2, edges)
        self.assertIn(edge3, edges)
        self.assertIn(edge4, edges)
        self.assertNotIn(edge1, edges)

    def test_find_edge(self):
        self.assertEqual(0, self.graph.count_edges())
        
        edge1 = {DST: 'b', EDGE: '111', TIMESTAMP: 111}
        self.graph.add_edge("a", edge1)
        edge2 = {DST: 'c', EDGE: '222', TIMESTAMP: 333}
        self.graph.add_edge("b", edge2)
        edge3 = {DST: 'd', EDGE: '333', TIMESTAMP: 222}
        self.graph.add_edge("b", edge3)
        edge4 = {DST: 'e', EDGE: '444', TIMESTAMP: 111}
        self.graph.add_edge("b", edge4)
        
        edge = self.graph.find_edge("b")
        self.assertIn(edge4, [ edge ])
        self.assertNotIn(edge1, [ edge ])
        self.assertNotIn(edge2, [ edge ])
        self.assertNotIn(edge3, [ edge ])


    def test_find_edges_xy(self):
        self.assertEqual(0, self.graph.count_edges())
        
        edge1 = {DST: 'B', EDGE: '1'}
        edge2 = {DST: 'C', EDGE: '2'}
        edge3 = {DST: 'E', EDGE: '3'}
        self.graph.add_edge("A", edge1)
        self.graph.add_edge("A", edge2)
        self.graph.add_edge("A", edge3)
       
        edge4 = {DST: 'D', EDGE: '4'}
        edge5 = {DST: 'F', EDGE: '5'}
        self.graph.add_edge("B", edge4)
        self.graph.add_edge("B", edge5)
       
        edge6 = {DST: 'G', EDGE: '6'}
        self.graph.add_edge("C", edge6)

        edge13 = {DST: 'A', EDGE: '13'}
        self.graph.add_edge("E", edge13)

        edge7 = {DST: 'H', EDGE: '7'}
        edge8 = {DST: 'I', EDGE: '8'}
        self.graph.add_edge("D", edge7)
        self.graph.add_edge("D", edge8)
       
        edge9 = {DST: 'E', EDGE: '9'}
        self.graph.add_edge("F", edge9)
        
        edge10 = {DST: 'F', EDGE: '10'}
        self.graph.add_edge("G", edge10)

        edge11 = {DST: 'H', EDGE: '11'}
        edge12 = {DST: 'F', EDGE: '12'}
        edge14 = {DST: 'F', EDGE: '14'}
        self.graph.add_edge("I", edge11)
        self.graph.add_edge("I", edge12)
        self.graph.add_edge("I", edge14)
 
        edges = self.graph.find_edges_xy("I","F")
        self.assertIn(edge12, edges)
        self.assertIn(edge14, edges)

        self.assertNotIn(edge13, edges)
        self.assertNotIn(edge11, edges)
        self.assertNotIn(edge10, edges)
        self.assertNotIn(edge9, edges)
        self.assertNotIn(edge8, edges)
        self.assertNotIn(edge7, edges)
        self.assertNotIn(edge6, edges)
        self.assertNotIn(edge5, edges)
        self.assertNotIn(edge4, edges) 
        self.assertNotIn(edge3, edges)
        self.assertNotIn(edge2, edges)
        self.assertNotIn(edge1, edges)

    def test_find_edge_x2y(self):
        self.assertEqual(0, self.graph.count_edges())
        
        edge1 = {DST: 'B', EDGE: '1'}
        edge2 = {DST: 'C', EDGE: '2'}
        edge3 = {DST: 'E', EDGE: '3'}
        self.graph.add_edge("A", edge1)
        self.graph.add_edge("A", edge2)
        self.graph.add_edge("A", edge3)
       
        edge4 = {DST: 'D', EDGE: '4'}
        edge5 = {DST: 'F', EDGE: '5'}
        self.graph.add_edge("B", edge4)
        self.graph.add_edge("B", edge5)
       
        edge6 = {DST: 'G', EDGE: '6'}
        self.graph.add_edge("C", edge6)

        edge13 = {DST: 'A', EDGE: '13'}
        self.graph.add_edge("E", edge13)

        edge7 = {DST: 'H', EDGE: '7'}
        edge8 = {DST: 'I', EDGE: '8'}
        self.graph.add_edge("D", edge7)
        self.graph.add_edge("D", edge8)
       
        edge9 = {DST: 'E', EDGE: '9'}
        self.graph.add_edge("F", edge9)
        
        edge10 = {DST: 'F', EDGE: '10'}
        self.graph.add_edge("G", edge10)

        edge11 = {DST: 'H', EDGE: '11'}
        edge12 = {DST: 'F', EDGE: '12'}
        edge14 = {DST: 'F', EDGE: '14'}
        self.graph.add_edge("I", edge11)
        self.graph.add_edge("I", edge12)
        self.graph.add_edge("I", edge14)
 
        edges = self.graph.find_edge_x2y("A","F",2)
        self.assertIn(edge1, edges)
        self.assertIn(edge5, edges)

        self.assertNotIn(edge14, edges)
        self.assertNotIn(edge13, edges)
        self.assertNotIn(edge12, edges)
        self.assertNotIn(edge11, edges)
        self.assertNotIn(edge10, edges)
        self.assertNotIn(edge9, edges)
        self.assertNotIn(edge8, edges)
        self.assertNotIn(edge7, edges)
        self.assertNotIn(edge6, edges)
        self.assertNotIn(edge4, edges) 
        self.assertNotIn(edge3, edges)
        self.assertNotIn(edge2, edges)

    def test_find_edges_x2y(self):
        self.assertEqual(0, self.graph.count_edges())
        
        edge1 = {DST: 'B', EDGE: '1'}
        edge2 = {DST: 'C', EDGE: '2'}
        edge3 = {DST: 'E', EDGE: '3'}
        self.graph.add_edge("A", edge1)
        self.graph.add_edge("A", edge2)
        self.graph.add_edge("A", edge3)
       
        edge4 = {DST: 'D', EDGE: '4'}
        edge5 = {DST: 'F', EDGE: '5'}
        self.graph.add_edge("B", edge4)
        self.graph.add_edge("B", edge5)
       
        edge6 = {DST: 'G', EDGE: '6'}
        self.graph.add_edge("C", edge6)

        edge13 = {DST: 'A', EDGE: '13'}
        self.graph.add_edge("E", edge13)

        edge7 = {DST: 'H', EDGE: '7'}
        edge8 = {DST: 'I', EDGE: '8'}
        self.graph.add_edge("D", edge7)
        self.graph.add_edge("D", edge8)
       
        edge9 = {DST: 'E', EDGE: '9'}
        self.graph.add_edge("F", edge9)
        
        edge10 = {DST: 'F', EDGE: '10'}
        self.graph.add_edge("G", edge10)

        edge11 = {DST: 'H', EDGE: '11'}
        edge12 = {DST: 'F', EDGE: '12'}
        edge14 = {DST: 'F', EDGE: '14'}
        self.graph.add_edge("I", edge11)
        self.graph.add_edge("I", edge12)
        self.graph.add_edge("I", edge14)
 
        edgeslist = self.graph.find_edges_x2y("A","F",4)
        self.assertTrue(len(edgeslist) == 5, "Invalid number of Paths")

        #self.assertIn(edge7, edgeslist)               
 
        for edges in edgeslist:
            for edge in edges:
                if edge[SRC] == "G":
                    self.assertIn(edge2, edges)
                    self.assertIn(edge6, edges)
                    self.assertIn(edge10, edges)
                               
                    self.assertNotIn(edge1, edges)
                    self.assertNotIn(edge3, edges)
                    self.assertNotIn(edge4, edges)
                    self.assertNotIn(edge5, edges)
                    self.assertNotIn(edge7, edges)
                    self.assertNotIn(edge8, edges)
                    self.assertNotIn(edge9, edges)
                    self.assertNotIn(edge11, edges)
                    self.assertNotIn(edge12, edges)
                    self.assertNotIn(edge13, edges)
                    self.assertNotIn(edge14, edges)
                    
                if edge[SRC] == "I":
                    self.assertIn(edge1, edges)
                    self.assertIn(edge4, edges)
                    self.assertIn(edge8, edges)
                    
                    #self.assertIn(edge12, edges)
                    #self.assertIn(edge14, edges)
                    
                    self.assertNotIn(edge2, edges)
                    self.assertNotIn(edge3, edges)
                    self.assertNotIn(edge5, edges)
                    self.assertNotIn(edge6, edges)
                    self.assertNotIn(edge7, edges)
                    self.assertNotIn(edge9, edges)
                    self.assertNotIn(edge10, edges)
                    self.assertNotIn(edge11, edges)
                    self.assertNotIn(edge13, edges)

                if edge[SRC] == "E":
                    self.assertIn(edge3, edges)
                    self.assertIn(edge13, edges)
                    self.assertIn(edge1, edges)
                    self.assertIn(edge5, edges)
                               
                    self.assertNotIn(edge2, edges)
                    self.assertNotIn(edge4, edges)
                    self.assertNotIn(edge6, edges)
                    self.assertNotIn(edge7, edges)
                    self.assertNotIn(edge8, edges)
                    self.assertNotIn(edge9, edges)
                    self.assertNotIn(edge10, edges)
                    self.assertNotIn(edge11, edges)
                    self.assertNotIn(edge12, edges)
                    self.assertNotIn(edge14, edges)


            self.assertNotIn(edge7, edges)



"""
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
"""
