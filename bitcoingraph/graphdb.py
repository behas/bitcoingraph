
from bitcoingraph.neo4j import Neo4jController
from bitcoingraph.helper import to_time, to_json


class GraphController:

    rows_per_page_default = 20

    def __init__(self, host, port, user, password):
        self.graph_db = Neo4jController(host, port, user, password)

    def get_address_info(self, address, date_from=None, date_to=None,
                         rows_per_page=rows_per_page_default):
        result = self.graph_db.address_stats_query(address).single_row()
        if result['num_transactions'] == 0:
            return {'transactions': 0}
        if date_from is None and date_to is None:
            count = result['num_transactions']
        else:
            count = self.graph_db.address_count_query(address, date_from, date_to).single_result()
        entity = self.graph_db.entity_query(address).single_result()
        return {'transactions': result['num_transactions'],
                'first': to_time(result['first'], True),
                'last': to_time(result['last'], True),
                'entity': entity,
                'pages': (count + rows_per_page - 1) // rows_per_page}

    def get_received_bitcoins(self, address):
        return self.graph_db.get_received_bitcoins(address)

    def get_unspent_bitcoins(self, address):
        return self.graph_db.get_unspent_bitcoins(address)

    def get_address(self, address, page, date_from=None, date_to=None,
                    rows_per_page=rows_per_page_default):
        if rows_per_page is None:
            query = self.graph_db.address_query(address, date_from, date_to)
        else:
            query = self.graph_db.paginated_address_query(address, date_from, date_to,
                                                          page * rows_per_page, rows_per_page)
        return Address(address, self.get_identities(address), query.get())

    def get_identities(self, address):
        identities = self.graph_db.identity_query(address).single_result()
        return identities

    def get_entity(self, id, max_addresses=rows_per_page_default):
        count = self.graph_db.get_number_of_addresses_for_entity(id)
        result = self.graph_db.entity_address_query(id, max_addresses)
        entity = {'id': id, 'addresses': result.get(), 'number_of_addresses': count}
        return entity

    def search_address_by_identity_name(self, name):
        address = self.graph_db.reverse_identity_query(name).single_result()
        return address

    def add_identity(self, address, name, link, source):
        self.graph_db.identity_add_query(address, name, link, source)

    def delete_identity(self, id):
        self.graph_db.identity_delete_query(id)

    def get_path(self, address1, address2):
        return Path(self.graph_db.path_query(address1, address2))

    def get_max_block_height(self):
        return self.graph_db.get_max_block_height()

    def add_block(self, block):
        print('add block', block.height)
        with self.graph_db.transaction() as db_transaction:
            block_node_id = db_transaction.add_block(block)
            for index, tx in enumerate(block.transactions):
                print('add transaction {} of {} (txid: {})'.format(
                    index + 1, len(block.transactions), tx.txid))
                tx_node_id = db_transaction.add_transaction(block_node_id, tx)
                if not tx.is_coinbase():
                    for input in tx.inputs:
                        db_transaction.add_input(tx_node_id, input.output_reference)
                for output in tx.outputs:
                    output_node_id = db_transaction.add_output(tx_node_id, output)
                    for address in output.addresses:
                        db_transaction.add_address(output_node_id, address)
        print('create entities for block (node id: {})'.format(block_node_id))
        self.graph_db.create_entities(block_node_id)


class Address:

    def __init__(self, address, identities, outputs):
        self.address = address
        self.identities = identities
        self.outputs = [{'txid': o['txid'], 'value': o['value'],
                         'timestamp': to_time(o['timestamp'])}
                        for o in outputs]

    def get_incoming_transactions(self):
        for output in self.outputs:
            if output['value'] > 0:
                yield output

    def get_outgoing_transactions(self):
        for output in self.outputs:
            if output['value'] < 0:
                yield {'txid': output['txid'], 'value': -output['value'],
                       'timestamp': output['timestamp']}

    def to_graph_json(self):
        def value_sum(transactions):
            return sum([trans['value'] for trans in transactions])
        label = 'known_address' if self.identities else 'address'
        nodes = [{'label': label, 'address': self.address}]
        links = []
        incoming_transactions = list(self.get_incoming_transactions())
        outgoing_transactions = list(self.get_outgoing_transactions())
        if len(incoming_transactions) <= 10:
            for transaction in incoming_transactions:
                nodes.append({'label': 'transaction', 'txid': transaction['txid'],
                              'type': 'source'})
                links.append({'source': len(nodes) - 1, 'target': 0,
                              'value': transaction['value']})
        else:
            nodes.append({'label': 'transaction', 'amount': len(incoming_transactions),
                          'type': 'source'})
            links.append({'source': len(nodes) - 1, 'target': 0,
                          'type': 'OUTPUT', 'value': value_sum(incoming_transactions)})
        if len(outgoing_transactions) <= 10:
            for transaction in outgoing_transactions:
                nodes.append({'label': 'transaction', 'txid': transaction['txid'],
                              'type': 'target'})
                links.append({'source': 0, 'target': len(nodes) - 1,
                              'value': transaction['value']})
        else:
            nodes.append({'label': 'transaction', 'amount': len(outgoing_transactions),
                          'type': 'target'})
            links.append({'source': 0, 'target': len(nodes) - 1,
                          'type': 'INPUT', 'value': value_sum(outgoing_transactions)})
        return to_json({'nodes': nodes, 'links': links})


class Path:

    def __init__(self, raw_path):
        self.raw_path = raw_path

    @property
    def path(self):
        if self.raw_path:
            path = []
            for idx, row in enumerate(self.raw_path):
                if 'txid' in row:
                    path.append(row)
                else:
                    output = row
                    if idx != 0:
                        path.append(output)
                    path.append({'address': row['addresses'][0]})
                    if idx != len(self.raw_path) - 1:
                        path.append(output)
            return path
        else:
            return None
