
import requests


class GraphDB:

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url = 'http://{}:{}/db/data/transaction/commit'.format(host, port)

    def get_address(self, address):
        statement = 'MATCH (a:Address {address: {address}})-[r]-t RETURN a.address, t.txid, type(r), r.value'
        return Address(self.query(statement, {'address': address}))

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
            pass # maybe raise an exception here
        return r.json()


class Address:

    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def data(self):
        return self._raw_data['results'][0]['data']

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
        return {'txid': row[1], 'type': row[2], 'value': row[3]}


class Path:

    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def path(self):
        return self._raw_data['results'][0]['data'][0]['row'][0]
