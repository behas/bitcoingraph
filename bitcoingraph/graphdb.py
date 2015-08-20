
import requests
from bitcoingraph.blockchain import Address


class GraphDB:

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url = 'http://{}:{}/db/data/transaction/commit'.format(host, port)

    def get_address(self, address):
        return Address(self.address_query(address))

    def address_query(self, address):
        payload = {'statements': [{
            'statement': 'MATCH (a:Address {address: {address}})-[r]-t RETURN a.address, t.txid, type(r), r.value',
            'parameters': {'address': address}
        }]}
        headers = {
            'Accept': 'application/json; charset=UTF-8',
            'Content-Type': 'application/json'
        }
        r = requests.post(self.url, auth=(self.user, self.password), headers=headers, json=payload)
        return r.json()
