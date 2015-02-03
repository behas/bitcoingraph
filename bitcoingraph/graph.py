"""
Various types of graph views for the Bitcoin block chain.

"""

__author__ = ['Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)',
              'Aljosha Judmaier (aljosha@sba.ac.at)']
__copyright__ = 'Copyright 2015, Bernhard Haslhofer, Aljosha'
__license__ = "MIT"

import csv

from bitcoingraph.blockchain import BlockchainException


class GraphException(Exception):
    """
    Exception raised when interacting with blockchain graph view.
    """

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return repr(self.msg)


class Graph(object):
    """
    A generic directed graph representation.

    TODO: wrap third party library
    TODO: implement required graph search algorithms
    """
    def __init__(self):
        self._edges = []

    def add_edge(self, edge):
        """
        Add edge to graph.
        """
        self._edges.append(edge)

    def count_edges(self):
        """
        Returns number of edges in graph.
        """
        return len(self._edges)


class TransactionGraph(Graph):
    """
    A directed graph view on block chain transactions.

    Vertex = public key address (wallets)
    Edge = bitcoin flow from source to target address
    """

    def __init__(self, blockchain=None):
        """
        Creates transaction graph view on blockchain.
        """
        if blockchain is not None:
            self._blockchain = blockchain
        super().__init__()

    def load(self, start_block, end_block, tx_graph_file=None):
        """
        Loads transaction graph from blockchain or from transaction
        graph output file, if given.
        """
        if tx_graph_file:
            generator = self._generate_from_file(start_block,
                                                 end_block, tx_graph_file)
        else:
            generator = self._generate_from_blockchain(start_block, end_block)

        for edge in generator:
            self.add_edge(edge)

    def _generate_from_blockchain(self, start_block=None, end_block=None):
        """
        Generates transaction graph by extracting edges from blockchain.
        """
        if self._blockchain is None:
            raise GraphException("Cannot generated transaction graph without \
                reference to underlying blockchain")

        if start_block is None:
            start_block = 1
        if end_block is None:
            end_block = self._blockchain.get_max_blockheight()

        for block in self._blockchain.get_blocks_in_range(start_block,
                                                          end_block):
            for tx in block.transactions:
                try:
                    for bc_flow in tx.bc_flows:
                        # Construction transaction graph edge
                        edge = {}
                        edge['src'] = bc_flow['src']
                        edge['tgt'] = bc_flow['tgt']
                        # Addding named edge descriptior
                        edge['txid'] = tx.id
                        edge['value'] = bc_flow['value']
                        edge['timestamp'] = tx.time
                        edge['blockheight'] = block.height
                        yield edge
                except BlockchainException as exc:
                    raise GraphException("Transaction graph generation failed",
                                         exc)

    def _generate_from_file(self, start_block, end_block, tx_graph_file):
        """
        Generates transaction graph by loading edges from CSV file.
        """
        with open(tx_graph_file, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile, delimiter=';',
                                            quotechar='|',
                                            quoting=csv.QUOTE_MINIMAL)
                for edge in csv_reader:
                    yield edge

    def export_to_csv(self, start_block=None,
                      end_block=None, output_file=None, progress=None):
        """
        Exports transaction graph to CSV file directly from blockchain.
        """
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['txid', 'src', 'tgt',
                          'value', 'timestamp', 'blockheight']
            csv_writer = csv.DictWriter(csvfile, delimiter=';', quotechar='|',
                                        fieldnames=fieldnames,
                                        quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()
            for edge in self._generate_from_blockchain(start_block, end_block):
                csv_writer.writerow(edge)
                if progress:
                    progress(edge['blockheight'] / (end_block - start_block))


class EntityGraph(Graph):
    """
    A directed graph view on entites in the blockchain.

    Vertex = entity
    Edge = bitcoin flow between entities
    """

    def __init__(self, tx_graph=None):
        """
        Creates entity graph view based on transaction graph.
        """
        if tx_graph is not None:
            self._tx_graph = tx_graph
        super().__init__()

    def _generate_from_file(self, et_graph_file):
        """
        TODO: Generates entity graph by loading edges from CSV file.
        """
        pass

    def generate_from_tx_graph(self):
        """
        TODO: Generate entity graph by computing union-find over transaction
        graph.
        """
        pass

    def export_to_csv(self, output_file, progress=None):
        """
        Exports entity graph to CSV file.
        """
        pass
