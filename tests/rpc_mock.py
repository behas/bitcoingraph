from bitcoingraph.rpc import BitcoinProxy


class BitcoinProxyMock(BitcoinProxy):

    """Proxy to Bitcoin RPC Service implementing Bitcoin client call list
    https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_Calls_list"""
    def __init__(self, url):
        super().__init__(url)

    def getblock(self, hash):
        print("Hey, called getblock!")

    def getblockcount(self):
        print("Hey, called getblockcount!")

    def getblockhash(self, index):
        print("Hey, called getblockhash!")

    def getinfo(self):
        print("Hey, called getinfo!")

    def getrawtransaction(self, tx_id, verbose=1):
        print("Hey, called getrawtransaction!")
