
import requests
from datetime import date, datetime, timezone


def lb_join(*lines):
    return '\n'.join(lines)


class GraphDB:

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url_base = 'http://{}:{}/db/data/'.format(host, port)
        self.url = self.url_base + 'transaction/commit'

    address_match = lb_join(
        'MATCH (a:Address {address: {address}})<-[:USES]-(o)-[r:INPUT|OUTPUT]-(t)<-[:CONTAINS]-(b)',
        'WITH a, t, type(r) AS rel_type, sum(o.value) AS value, b')
    address_period_match = lb_join(
        address_match,
        'WHERE b.timestamp > {from} AND b.timestamp < {to}')
    address_statement = lb_join(
        address_period_match,
        'RETURN t.txid as txid, rel_type as type, value as value, b.timestamp as timestamp',
        'ORDER BY b.timestamp desc')
    entity_match = lb_join(
        'MATCH (e:Entity)<-[:BELONGS_TO]-(a)',
        'WHERE id(e) = {id}')

    def address_stats_query(self, address):
        s = lb_join(
            self.address_match,
            'RETURN count(*) as num_transactions, min(b.timestamp) as first, max(b.timestamp) as last')
        return self.query(s, {'address': address})

    def address_count_query(self, address, date_from, date_to):
        s = lb_join(
            self.address_period_match,
            'RETURN count(*)')
        return self.query(s, self.as_address_query_parameter(address, date_from, date_to))

    def address_query(self, address, date_from, date_to):
        return self.query(self.address_statement, self.as_address_query_parameter(address, date_from, date_to))

    def paginated_address_query(self, address, date_from, date_to, skip, limit):
        s = lb_join(
            self.address_statement,
            'SKIP {skip} LIMIT {limit}')
        p = self.as_address_query_parameter(address, date_from, date_to)
        p['skip'] = skip
        p['limit'] = limit
        return self.query(s, p)

    def entity_query(self, address):
        s = lb_join(
            'MATCH (a:Address {address: {address}})-[:BELONGS_TO]->(e)',
            'RETURN {id: id(e)}')
        return self.query(s, {'address': address})

    def entity_count_query(self, id):
        s = lb_join(
            self.entity_match,
            'RETURN count(*)')
        return self.query(s, {'id': id})

    def entity_address_query(self, id, limit):
        s = lb_join(
            self.entity_match,
            'OPTIONAL MATCH (a)-[:HAS]->(i)',
            'WITH e, a, collect(i) as is',
            'ORDER BY length(is) desc',
            'LIMIT {limit}',
            'RETURN a.address as address, is as identities')
        return self.query(s, {'id': id, 'limit': limit})

    def identity_query(self, address):
        s = lb_join(
            'MATCH (a:Address {address: {address}})-[:HAS]->(i)',
            'RETURN collect({id: id(i), name: i.name, link: i.link, source: i.source})')
        return self.query(s, {'address': address})

    def reverse_identity_query(self, name):
        s = lb_join(
            'MATCH (i:Identity {name: {name}})<-[:HAS]-(a)',
            'RETURN a.address')
        return self.query(s, {'name': name})

    def identity_add_query(self, address, name, link, source):
        s = lb_join(
            'MATCH (a:Address {address: {address}})',
            'CREATE (a)-[:HAS]->(i:Identity {name: {name}, link: {link}, source: {source}})')
        return self.query(s, {'address': address, 'name': name, 'link': link, 'source': source})

    def identity_delete_query(self, id):
        s = lb_join(
            'MATCH (i:Identity)',
            'WHERE id(i) = {id}',
            'DETACH DELETE i')
        return self.query(s, {'id': id})

    def path_query(self, address1, address2):
        s = lb_join(
            'MATCH (start:Address {address: {address1}})<-[:USES]-(o1:Output)',
            '  -[:INPUT|OUTPUT*]->(o2:Output)-[:USES]->(end:Address {address: {address2}}),',
            '  p = shortestpath((o1)-[:INPUT|OUTPUT*]->(o2))',
            'WITH p',
            'LIMIT 1',
            'UNWIND nodes(p) as n',
            'OPTIONAL MATCH (n)-[:USES]->(a)',
            'RETURN n as node, a as address')
        return self.query(s, {'address1': address1, 'address2': address2})

    def get_max_block_height(self):
        s = lb_join(
            'MATCH (b:Block)',
            'RETURN max(b.height)')
        return self.query(s).single_result()

    def add_block(self, block):
        s = lb_join(
            'CREATE (b:Block {hash: {hash}, height: {height}, timestamp: {timestamp}})',
            'RETURN id(b)')
        return self.query(s, {'hash': block.hash, 'height': block.height, 'timestamp': block.timestamp}).single_result()

    def add_transaction(self, block_node_id, tx):
        s = lb_join(
            'MATCH (b) WHERE id(b) = {id}',
            'CREATE (b)-[:CONTAINS]->(t:Transaction {txid: {txid}, coinbase: {coinbase}})',
            'RETURN id(t)')
        return self.query(s, {'id': block_node_id, 'txid': tx.txid, 'coinbase': tx.is_coinbase()}).single_result()

    def add_input(self, tx_node_id, output_reference):
        s = lb_join(
            'MATCH (o:Output {txid_n: {txid_n}}), (t)',
            'WHERE id(t) = {id}',
            'CREATE (o)-[:INPUT]->(t)')
        return self.query(s, {'txid_n': '{}_{}'.format(output_reference['txid'], output_reference['vout']),
                              'id': tx_node_id}).single_result()

    def add_output(self, tx_node_id, output):
        s = lb_join(
            'MATCH (t) WHERE id(t) = {id}',
            'CREATE (t)-[:OUTPUT]->(o:Output {txid_n: {txid_n}, n: {n}, value: {value}, type: {type}})',
            'RETURN id(o)')
        return self.query(s, {'id': tx_node_id, 'txid_n': '{}_{}'.format(output.transaction.txid, output.index),
                              'n': output.index, 'value': output.value, 'type': output.type}).single_result()

    def add_address(self, output_node_id, address):
        s = lb_join(
            'MATCH (o) WHERE id(o) = {id}',
            'MERGE (a:Address {address: {address}})',
            'CREATE (o)-[:USES]->(a)',
            'RETURN id(a)')
        return self.query(s, {'id': output_node_id, 'address': address}).single_result()

    def create_entity(self, transaction_node_id):
        url = self.url_base + 'ext/Entity/node/{}/createEntity'.format(transaction_node_id)
        requests.post(url, auth=(self.user, self.password))

    def query(self, statement, parameters=None):
        statement_json = {'statement': statement}
        if parameters is not None:
            statement_json['parameters'] = parameters
        payload = {'statements': [statement_json]}
        headers = {
            'Accept': 'application/json; charset=UTF-8',
            'Content-Type': 'application/json',
            'max-execution-time': 30000
        }
        r = requests.post(self.url, auth=(self.user, self.password), headers=headers, json=payload)
        if r.status_code != 200:
            pass  # maybe raise an exception here
        return QueryResult(r.json())

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


class QueryResult:

    def __init__(self, raw_data):
        self._raw_data = raw_data

    def data(self):
        if self._raw_data['results']:
            return self._raw_data['results'][0]['data']
        else:
            return []

    def columns(self):
        return self._raw_data['results'][0]['columns']

    def get(self):
        return [dict(zip(self.columns(), r['row'])) for r in self.data()]

    def list(self):
        return [r['row'][0] for r in self.data()]

    def single_result(self):
        if self.data():
            return self.data()[0]['row'][0]
        else:
            return None

    def single_row(self):
        rows = self.get()
        if self.get():
            return list(self.get())[0]
        else:
            return None
