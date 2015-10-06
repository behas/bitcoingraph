
from datetime import date, datetime, timezone
import requests
from bitcoingraph.blockchain import to_json, to_time


class GraphDB:

    address_match = '''MATCH (a:Address {address: {address}})-[r:INPUT|OUTPUT]-t
        WITH a, t, type(r) AS rel_type, sum(r.value) AS value
        '''

    address_period_match = address_match + 'WHERE t.timestamp > {from} AND t.timestamp < {to}\n'
    rows_per_page_default = 20

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url = 'http://{}:{}/db/data/transaction/commit'.format(host, port)

    def get_address_info(self, address, date_from=None, date_to=None, rows_per_page=rows_per_page_default):
        statement = GraphDB.address_match + 'RETURN count(*), min(t.timestamp), max(t.timestamp)'
        result_row = self.single_row_query(statement, {'address': address})
        num_transactions = result_row[0]
        if num_transactions == 0:
            return {'transactions': 0}
        if date_from is None and date_to is None:
            count = num_transactions
        else:
            parameter = self.as_address_query_parameter(address, date_from, date_to)
            count = self.single_result_query(GraphDB.address_period_match + 'RETURN count(*)', parameter)
        entity_statement = 'MATCH (a:Address {address: {address}})-[:BELONGS_TO]->e RETURN e, id(e)'
        result = self.single_row_query(entity_statement, {'address': address})
        entity = result[0]
        entity['id'] = result[1]
        return {'transactions': num_transactions,
                'first': to_time(result_row[1], True),
                'last': to_time(result_row[2], True),
                'entity': entity,
                'pages': (count + rows_per_page - 1) // rows_per_page}

    def get_address(self, address, page, date_from=None, date_to=None, rows_per_page=rows_per_page_default):
        statement = GraphDB.address_period_match + '''RETURN a.address, t.txid, rel_type, value, t.timestamp
                ORDER BY t.timestamp desc'''
        parameter = self.as_address_query_parameter(address, date_from, date_to)
        if rows_per_page is not None:
            statement += '\nSKIP {skip} LIMIT {limit}'
            parameter['skip'] = page * rows_per_page
            parameter['limit'] = rows_per_page
        return Address(self.query(statement, parameter))

    @staticmethod
    def as_address_query_parameter(address, date_from=None, date_to=None):
        if date_from is None:
            timestamp_from = 0
        else:
            timestamp_from = datetime.strptime(date_from, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()
        if date_to is None:
            timestamp_to = 2 ** 31 - 1
        else:
            d = datetime.strptime(date_to, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            d += date.resolution
            timestamp_to = d.timestamp()
        return {'address': address, 'from': timestamp_from, 'to': timestamp_to}

    def get_entity(self, id, max_addresses=rows_per_page_default):
        count_statement = 'MATCH (e:Entity)--a WHERE id(e) = {id} RETURN count(*)'
        statement = 'MATCH (e:Entity)--a WHERE id(e) = {id} WITH e, a LIMIT {limit} RETURN e, collect(a.address)'
        count = self.single_result_query(count_statement, {'id': id})
        result = self.single_row_query(statement, {'id': id, 'limit': max_addresses})
        entity = result[0]
        entity['id'] = id
        entity['addresses'] = result[1]
        entity['number_of_addresses'] = count
        return entity

    def search_entity_by_name(self, name):
        statement = 'MATCH (e:Entity {name: {name}}) RETURN id(e)'
        id = self.single_result_query(statement, {'name': name})
        return id

    def update_entity(self, id, name, link):
        entity_statement = 'MATCH (e:Entity) WHERE id(e) = {id} SET e.name = {name}, e.link = {link}'
        self.query(entity_statement, {'id': id, 'name': name, 'link': link})

    def get_path(self, address1, address2):
        statement = '''MATCH p = shortestpath (
                (start:Address {address: {address1}})-[*]->(end:Address {address: {address2}})
            ) RETURN p'''
        return Path(self.query(statement, {'address1': address1, 'address2': address2}))

    def query(self, statement, parameters):
        payload = {'statements': [{
            'statement': statement,
            'parameters': parameters
        }]}
        headers = {
            'Accept': 'application/json; charset=UTF-8',
            'Content-Type': 'application/json'
        }
        r = requests.post(self.url, auth=(self.user, self.password), headers=headers, json=payload)
        if r.status_code != 200:
            pass  # maybe raise an exception here
        return r.json()

    def single_row_query(self, statement, parameters):
        query_result = self.query(statement, parameters)
        data = query_result['results'][0]['data']
        if data:
            return data[0]['row']
        else:
            return None

    def single_result_query(self, statement, parameters):
        first_row = self.single_row_query(statement, parameters)
        if first_row is None:
            return None
        else:
            return first_row[0]


class QueryResult:

    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def data(self):
        return self._raw_data['results'][0]['data']

    @staticmethod
    def convert_row(raw_data):
        row = raw_data['row']
        return row[0]

    def get_list(self):
        return map(self.convert_row, self.data)


class Address(QueryResult):

    @property
    def address(self):
        if not self.data:
            return None
        return self.data[0]['row'][0]

    @property
    def bc_flows(self):
        return map(self.convert_row, self.data)

    @staticmethod
    def convert_row(raw_data):
        row = raw_data['row']
        return {'txid': row[1], 'type': row[2], 'value': row[3], 'timestamp': to_time(row[4])}

    def get_transactions(self):
        return self.bc_flows

    def get_incoming_transactions(self):
        for transaction in self.get_transactions():
            if transaction['type'] == 'OUTPUT':
                yield transaction

    def get_outgoing_transactions(self):
        for transaction in self.get_transactions():
            if transaction['type'] == 'INPUT':
                yield transaction

    def get_graph_json(self):
        def value_sum(transactions):
            return sum([trans['value'] for trans in transactions])
        nodes = [{'label': 'Address', 'address': self.address}]
        links = []
        incoming_transactions = list(self.get_incoming_transactions())
        outgoing_transactions = list(self.get_outgoing_transactions())
        if len(incoming_transactions) <= 10:
            for transaction in incoming_transactions:
                nodes.append({'label': 'Transaction', 'txid': transaction['txid'], 'type': 'source'})
                links.append({'source': len(nodes) - 1, 'target': 0,
                              'type': transaction['type'], 'value': transaction['value']})
        else:
            nodes.append({'label': 'Transaction', 'amount': len(incoming_transactions), 'type': 'source'})
            links.append({'source': len(nodes) - 1, 'target': 0,
                          'type': 'OUTPUT', 'value': value_sum(incoming_transactions)})
        if len(outgoing_transactions) <= 10:
            for transaction in outgoing_transactions:
                nodes.append({'label': 'Transaction', 'txid': transaction['txid'], 'type': 'target'})
                links.append({'source': 0, 'target': len(nodes) - 1,
                              'type': transaction['type'], 'value': transaction['value']})
        else:
            nodes.append({'label': 'Transaction', 'amount': len(outgoing_transactions), 'type': 'target'})
            links.append({'source': 0, 'target': len(nodes) - 1,
                          'type': 'INPUT', 'value': value_sum(outgoing_transactions)})
        return to_json({'nodes': nodes, 'links': links})


class Path:

    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def path(self):
        if self._raw_data['results'][0]['data']:
            return self._raw_data['results'][0]['data'][0]['row'][0]
        else:
            return None

    def get_graph_json(self):
        nodes = []
        links = []
        for pc in self.path:
            if 'address' in pc:
                nodes.append({'label': 'Address', 'address': pc['address']})
            elif 'txid' in pc:
                nodes.append({'label': 'Transaction', 'txid': pc['txid']})
            else:
                links.append({'source': len(nodes) - 1, 'target': len(nodes), 'value': pc['value']})
        return to_json({'nodes': nodes, 'links': links})
