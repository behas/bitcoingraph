"""
bitcoingraph

A Python library for extracting and navigating graph structures from
the Bitcoin block chain.

"""

import logging

from bitcoingraph.bitcoind import BitcoinProxy, BitcoindException
from bitcoingraph.blockchain import Blockchain
from bitcoingraph import entities
from bitcoingraph.graphdb import GraphController
from bitcoingraph.helper import sort
from bitcoingraph.writer import CSVDumpWriter

logger = logging.getLogger('bitcoingraph')


class BitcoingraphException(Exception):
    """
    Top-level exception raised when interacting with bitcoingraph
    library.
    """

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return self.msg


class BitcoinGraph:
    """Facade which provides the main access to this package."""

    def __init__(self, **config):
        """Create an instance based on the configuration."""
        self.blockchain = self.__get_blockchain(config['blockchain'])
        if 'neo4j' in config:
            nc = config['neo4j']
            self.graph_db = GraphController(nc['host'], nc['port'], nc['user'], nc['pass'])

    @staticmethod
    def __get_blockchain(config):
        """Connect to Bitcoin Core (via JSON-RPC) and return a
        Blockchain object.
        """
        try:
            logger.debug("Connecting to Bitcoin Core at {}".format(config['host']))
            bc_proxy = BitcoinProxy(**config)
            bc_proxy.getinfo()
            logger.debug("Connection successful.")
            blockchain = Blockchain(bc_proxy)
            return blockchain
        except BitcoindException as exc:
            raise BitcoingraphException("Couldn't connect to {}.".format(config['host']), exc)

    def get_transaction(self, tx_id):
        """Return a transaction."""
        return self.blockchain.get_transaction(tx_id)

    def incoming_addresses(self, address, date_from, date_to):
        return self.graph_db.incoming_addresses(address, date_from, date_to)

    def outgoing_addresses(self, address, date_from, date_to):
        return self.graph_db.outgoing_addresses(address, date_from, date_to)

    def transaction_relations(self, address1, address2, date_from=None, date_to=None):
        return self.graph_db.transaction_relations(address1, address2, date_from, date_to)

    def get_block_by_height(self, height):
        """Return the block for a given height."""
        return self.blockchain.get_block_by_height(height)

    def get_block_by_hash(self, hash):
        """Return a block."""
        return self.blockchain.get_block_by_hash(hash)

    def search_address_by_identity_name(self, term):
        """Return an address that has an associated identity with
        the given name.
        """
        return self.graph_db.search_address_by_identity_name(term)

    def get_address_info(self, address, date_from, date_to):
        """Return basic address information for the given
        time period.
        """
        return self.graph_db.get_address_info(address, date_from, date_to)

    def get_address(self, address, current_page, date_from, date_to,
                    rows_per_page=GraphController.rows_per_page_default):
        """Return an address with its transaction uses in a given
        time period.
        """
        return self.graph_db.get_address(address, current_page, date_from, date_to, rows_per_page)

    def get_identities(self, address):
        """Return a list of identities."""
        return self.graph_db.get_identities(address)

    def add_identity(self, address, name, link, source):
        """Add an identity to an address."""
        self.graph_db.add_identity(address, name, link, source)

    def delete_identity(self, identity_id):
        """Delete an identity."""
        return self.graph_db.delete_identity(identity_id)

    def get_entity(self, id):
        """Return an entity."""
        return self.graph_db.get_entity(id)

    def get_path(self, start, end):
        """Return a path between addresses."""
        return self.graph_db.get_path(start, end)

    def get_received_bitcoins(self, address):
        """Return the total number of bitcoins received by this address."""
        return self.graph_db.get_received_bitcoins(address)

    def get_unspent_bitcoins(self, address):
        """Return the current balance of this address."""
        return self.graph_db.get_unspent_bitcoins(address)

    def export(self, start, end, output_path=None, plain_header=False, separate_header=True,
               progress=None, deduplicate_transactions=True):
        """Export the blockchain into CSV files."""
        if output_path is None:
            output_path = 'blocks_{}_{}'.format(start, end)

        number_of_blocks = end - start + 1
        with CSVDumpWriter(output_path, plain_header, separate_header) as writer:
            for block in self.blockchain.get_blocks_in_range(start, end):
                writer.write(block)
                if progress:
                    processed_blocks = block.height - start + 1
                    last_percentage = ((processed_blocks - 1) * 100) // number_of_blocks
                    percentage = (processed_blocks * 100) // number_of_blocks
                    if percentage > last_percentage:
                        progress(processed_blocks / number_of_blocks)
        if separate_header:
            sort(output_path, 'addresses.csv', '-u')
            if deduplicate_transactions:
                for base_name in ['transactions', 'rel_tx_output',
                                  'outputs', 'rel_output_address']:
                    sort(output_path, base_name + '.csv', '-u')

    def synchronize(self, max_blocks=None):
        """Synchronise the graph database with the blockchain
        information from the bitcoin client.
        """
        start = self.graph_db.get_max_block_height() + 1
        blockchain_end = self.blockchain.get_max_block_height() - 2
        if start > blockchain_end:
            print('Already up-to-date.')
        else:
            if max_blocks is None:
                end = blockchain_end
            else:
                end = min(start + max_blocks - 1, blockchain_end)
            print('add blocks', start, 'to', end)
            for block in self.blockchain.get_blocks_in_range(start, end):
                self.graph_db.add_block(block)


def compute_entities(input_path, sort_input=False):
    """Read exported CSV files containing blockchain information and
    export entities into CSV files.
    """
    if sort_input:
        sort(input_path, 'rel_output_address.csv')
    sort(input_path, 'rel_input.csv', '-k 2 -t ,')
    entities.calculate_input_addresses(input_path)
    sort(input_path, 'input_addresses.csv')
    entities.compute_entities(input_path)
