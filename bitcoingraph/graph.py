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


class TransactionGraph(object):
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
        self._edges = []

    def generate_edges(self, start_block=None, end_block=None):
        """
        Generates transaction graph edges from blockchain.

        An edge consists of a source (src) and a target (tgt) value
        and a set of named edge descriptors.

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

    def export_to_csv(self, start_block=None,
                      end_block=None, output_file=None, progress=None):
        """
        Exports transaction graph to CSV file.
        """
        with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['txid', 'src_addr', 'tgt_addr', 'value',
                                 'timestamp', 'block_height'])
            for edge in self.generate_edges(start_block, end_block):
                src = edge['src']
                if src is None:
                    src = "NULL"
                tgt = edge['tgt']
                if tgt is None:
                    tgt = "NULL"
                csv_writer.writerow([edge['txid'], src, tgt, edge['value'],
                                    edge['timestamp'], edge['blockheight']])
                if progress:
                    progress(edge['blockheight'] / (end_block - start_block))

    def load(self, start_block, end_block, tx_graph_file=None):
        """
        Loads transaction graph from blockchain or from given transaction
        graph output file.
        """
        if tx_graph_file is None:
            for edge in self.generate_edges(start_block, end_block):
                self._edges = self._edges + edge
