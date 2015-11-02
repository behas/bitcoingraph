"""
bitcoingraph

A Python library for extracting and navigating graph structures from
the Bitcoin block chain.

"""

import logging

from bitcoingraph.blockchain import Blockchain
from bitcoingraph.graph_controller import GraphController
from bitcoingraph.bitcoind import BitcoinProxy, JSONRPCException
from bitcoingraph.writer import CSVDumpWriter

logger = logging.getLogger('bitcoingraph')


class BitcoingraphException(Exception):
    """
    Top-level exception raised when interacting with bitcoingraph library.
    """

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return self.msg


class BitcoinGraph:

    def __init__(self, **config):

        self.blockchain = self.__get_blockchain(config['blockchain'])
        if 'neo4j' in config:
            nc = config['neo4j']
            self.graph_db = GraphController(nc['host'], nc['port'], nc['user'], nc['pass'])

    # Blockchain interfaces
    @staticmethod
    def __get_blockchain(config):
        """
        Connects to Bitcoin Core (via JSON-RPC) and returns a Blockchain object.
        """

        try:
            logger.debug("Connecting to Bitcoin Core at {}".format(config['host']))
            bc_proxy = BitcoinProxy(**config)
            bc_proxy.getinfo()
            logger.debug("Connection successful.")
            blockchain = Blockchain(bc_proxy)
            return blockchain
        except JSONRPCException as exc:
            raise BitcoingraphException("Couldn't connect to {}.".format(config['host']), exc)

    def get_transaction(self, tx_id):
        return self.blockchain.get_transaction(tx_id)

    def get_block_by_height(self, height):
        return self.blockchain.get_block_by_height(height)

    def get_block_by_hash(self, hash):
        return self.blockchain.get_block_by_hash(hash)

    def search_address_by_identity_name(self, term):
        return self.graph_db.search_address_by_identity_name(term)

    def get_address_info(self, address, date_from, date_to):
        return self.graph_db.get_address_info(address, date_from, date_to)

    def get_address(self, address, current_page, date_from, date_to,
                    rows_per_page=GraphController.rows_per_page_default):
        return self.graph_db.get_address(address, current_page, date_from, date_to, rows_per_page)

    def get_identities(self, address):
        return self.graph_db.get_identities(address)

    def add_identity(self, address, name, link, source):
        return self.graph_db.add_identity(address, name, link, source)

    def delete_identity(self, identity_id):
        return self.graph_db.delete_identity(identity_id)

    def get_entity(self, id):
        return self.graph_db.get_entity(id)

    def get_path(self, start, end):
        return self.graph_db.get_path(start, end)

    def export(self, start, end, output_path=None, plain_header=False, separate_header=True, progress=None):
        if output_path is None:
            output_path = 'blocks_{}_{}'.format(start, end)

        number_of_blocks = end - start + 1
        with CSVDumpWriter(output_path, plain_header, separate_header) as writer:
            for block in self.blockchain.get_blocks_in_range(start, end):
                writer.write(block)
                if progress:
                    counter = block.height - start + 1
                    last_percentage = (counter * 100) // number_of_blocks
                    percentage = ((counter + 1) * 100) // number_of_blocks
                    if percentage > last_percentage:
                        progress((counter + 1) / number_of_blocks)
