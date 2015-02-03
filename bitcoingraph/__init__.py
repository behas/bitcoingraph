"""
bitcoingraph

A Python library for extracting and navigating graph structures from
the Bitcoin block chain.

"""

__author__ = 'Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)'
__copyright__ = 'Copyright 2015, Bernhard Haslhofer'
__license__ = "MIT"
__version__ = '0.1'

__all__ = ['export_tx_graph']


from bitcoingraph.graph import TransactionGraph


def export_tx_graph(blockchain, start_block, end_block,
                    output_file, progress=None):
    """
    Exports transaction graph from the block chain and saves it to a
    CSV file.

    :param BlockChain blockchain: instantiated blockchain object
    :param int start_block: start block of transaction export range
    :param int end_block: end block of transaction export range
    """
    tx_graph = TransactionGraph(blockchain)
    tx_graph.export_to_csv(start_block, end_block, output_file, progress)
