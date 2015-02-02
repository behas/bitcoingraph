"""
blockchain

An API for traversing the Bitcoin block chain

"""

__author__ = 'Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)'
__copyright__ = 'Copyright 2015, Bernhard Haslhofer'
__license__ = "MIT"

import json
import datetime as dt

from bitcoingraph.rpc import JSONRPCException


def to_json(raw_data):
    """
    Pretty-prints JSON data

    :param str raw_data: raw JSON data
    """
    return json.dumps(raw_data, sort_keys=True,
                      indent=4, separators=(',', ': '))


def to_time(numeric_string):
    """
    Converts UTC timestamp to string-formatted data time.

    :param int numeric_string: UTC timestamp
    """
    time_as_date = dt.datetime.utcfromtimestamp(int(numeric_string))
    return time_as_date.strftime('%Y-%m-%d %H:%M:%S')


class BlockchainException(Exception):
    """
    Exception raised when accessing or navigating the block chain.
    """

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return repr(self.msg)


class BlockchainObject(object):
    """
    Generic block chain object.
    """

    def __init__(self, raw_data, blockchain):
        """
        Creates a generic block chain object.

        :param str raw_data: raw JSON data extracted from block chain
        :param BlockChain blockchain: instantiated blockchain object
        :return: block chain object
        :rtype: BlockchainObject
        """
        self._raw_data = raw_data
        self._blockchain = blockchain

    @property
    def time(self):
        """
        UTC timestamp in UNIX-format denoting approximate creation time.

        :return: approximate creation time as UTC timestamp
        :rtype: str
        """
        return self._raw_data['time']

    @property
    def time_as_dt(self):
        """
        String-formatted approximate creation time.

        :return: approximate creation time
        :rtype: str
        """
        return to_time(self.time)

    def __str__(self):
        return to_json(self._raw_data)

    def __repr__(self):
        return to_json(self._raw_data)


class Block(BlockchainObject):

    """
    Bitcoin block recording transactions.
    """

    def __init__(self, raw_data, blockchain):
        """
        Creates a block object.

        :param str raw_data: raw JSON data extracted from block chain
        :param BlockChain blockchain: instantiated blockchain object
        :return: block object
        :rtype: Block
        """
        super().__init__(raw_data, blockchain)

    @property
    def height(self):
        """
        Number of blocks between it and genesis block (height 0).

        :return: block height
        :rtype: int
        """
        return int(self._raw_data['height'])

    @property
    def hash(self):
        """
        256-bit hash based on all of the transactions in the block.

        :return: block hash
        :rtype: str
        """
        return self._raw_data['hash']

    @property
    def nextblockhash(self):
        """
        Reference to the next block.

        :return: next block hash
        :rtype: str
        """
        return self._raw_data['nextblockhash']

    @property
    def hasnextblock(self):
        """
        Returns `True` if block references next block.
        """
        return 'nextblockhash' in self._raw_data

    @property
    def nextblock(self):
        """
        Returns next block.

        :return: next block or `None` if there is none
        :rtype: Block
        """
        if self.hasnextblock:
            block_hash = self.nextblockhash
            return self._blockchain.get_block_by_hash(block_hash)
        else:
            return None

    @property
    def tx_count(self):
        """
        Returns number of transactions in block.

        :return: number of transactions
        :rtype: int
        """
        return len(self._raw_data['tx'])

    @property
    def tx_ids(self):
        """
        Returns ids of transactions in block.

        :return: list of transaction ids
        :rtype: array
        """
        return self._raw_data['tx']

    @property
    def transactions(self):
        """
        Generates Transaction objects for each transaction in block.

        :yield: transaction
        :rtype: Transaction
        """
        for tx_id in self.tx_ids:
            yield self._blockchain.get_transaction(tx_id)


class TxInput(object):

    """
    Transaction input.
    """

    def __init__(self, raw_data, blockchain):
        """
        Creates a transaction input object.

        :param str raw_data: raw JSON data extracted from block chain
        :param BlockChain blockchain: instantiated blockchain object
        :return: transaction input object
        :rtype: TxInput
        """
        self._raw_data = raw_data
        self._blockchain = blockchain

    @property
    def is_coinbase(self):
        """
        Returns `True` if input refers to coinbase.
        """
        return 'coinbase' in self._raw_data

    @property
    def prev_tx_hash(self):
        """
        Returns hash of previous transaction or `None` if transaction
        is coinbase transaction.

        :return: previous transaction hash
        :rtype: str
        """
        if self.is_coinbase:
            return None
        else:
            return self._raw_data['txid']

    @property
    def prev_tx_output_index(self):
        """
        Returns index of output in previous transaction or `None` if
        transaction is coinbase transaction.

        :return: previous transaction output index
        :rtype: str
        """
        if self.is_coinbase:
            return None
        else:
            return self._raw_data['vout']

    @property
    def prev_tx_output(self):
        """
        Returns ouput in previous transaction or `None` if transaction
        is coinbase transaction.

        :return: previous transaction output
        :rtype: TxOutput
        """
        if self.is_coinbase:
            return None
        else:
            prev_tx = self._blockchain.get_transaction(self.prev_tx_hash)
            return prev_tx.get_output_by_index(self.prev_tx_output_index)

    @property
    def addresses(self):
        """
        Returns addresses in output in previous transaction or `None` if
        transaction is coinbase transaction.

        :return: previous transaction output addresses
        :rtype: array
        """
        if self.is_coinbase:
            return None
        else:
            return self.prev_tx_output.addresses


class TxOutput(object):

    """
    Transaction output.
    """

    def __init__(self, raw_data):
        """
        Creates a transaction output object.

        :param str raw_data: raw JSON data extracted from block chain
        :return: transaction output object
        :rtype: TxOutput
        """
        self._raw_data = raw_data

    @property
    def index(self):
        """
        Returns index of transaction output.

        :return: transaction output index
        :rtype: str
        """
        return self._raw_data['n']

    @property
    def value(self):
        """
        Returns amount of Bitcoins.

        :return: amount of Bitcoins
        :rtype: float
        """
        return float(self._raw_data['value'])

    @property
    def addresses(self):
        """
        Returns transaction output addresses or `None` if output has
        no recorded addresses.

        :return: output addresses
        :rtype: array
        """
        scriptPubKey = self._raw_data.get('scriptPubKey')
        if scriptPubKey is not None:
            return scriptPubKey.get('addresses')
        else:
            return None


class Transaction(BlockchainObject):

    """
    Bitcoin transaction.
    """

    def __init__(self, raw_data, blockchain):
        """
        Creates a transaction object.

        :param str raw_data: raw JSON data extracted from block chain
        :param BlockChain blockchain: instantiated blockchain object
        :return: transaction object
        :rtype: Transaction
        """
        super().__init__(raw_data, blockchain)

    # Explicit transaction properties

    @property
    def blocktime(self):
        """
        Returns blocktime as UTC timestamp.

        :return: blocktime as UTC timestamp
        :rtype: str
        """
        return self._raw_data['blocktime']

    @property
    def id(self):
        """
        Returns transaction id (hash)

        :return: transaction id (hash)
        :rtype: str
        """
        return self._raw_data['txid']

    # Input properties

    def get_inputs(self):
        """
        Generates transaction input objects for listed inputs.

        :yield: transaction input objects
        :rtype: TxInput
        """
        for tx_input in self._raw_data['vin']:
            yield TxInput(tx_input, self._blockchain)

    def get_input_count(self):
        """
        Returns number of listed transaction inputs.

        :return: transaction input count
        :rtype: int
        """
        if 'vin' in self._raw_data:
            return len(self._raw_data['vin'])
        else:
            return 0

    @property
    def is_coinbase_tx(self):
        """
        Returns `True` if transaction is coinbase transaction.
        """
        for tx_input in self.get_inputs():
            if tx_input.is_coinbase:
                return True
        else:
            return False

    # Output properties

    def get_output_count(self):
        """
        Returns number of listed transaction outputs.

        :return: transaction output count
        :rtype: int
        """
        if 'vout' in self._raw_data:
            return len(self._raw_data['vout'])
        else:
            return 0

    def get_outputs(self):
        """
        Generates transaction output objects for listed inputs.

        :yield: transaction output objects
        :rtype: TxOutput
        """
        for tx_output in self._raw_data['vout']:
            yield TxOutput(tx_output)

    def get_output_by_index(self, index):
        """
        Returns transaction output by id or `None` if there is none.

        :param int index: transaction output index
        :return: transaction output object
        :rtype: TxOutput
        """
        for output in self.get_outputs():
            if output.index == index:
                return output
        return None

    # Bitcoin flow properties

    @property
    def bc_flows(self):
        """
        Returns flows of Bitcoins between source and target addresses.

        :return: bitcoin flows (src, tgt, value)
        :rtype: array
        """
        bc_flows = []
        for tx_input in self.get_inputs():
            src = None
            if not self.is_coinbase_tx:
                if tx_input is None or tx_input.addresses is None:
                    src = None
                else:
                    src = tx_input.addresses[0]
            for tx_output in self.get_outputs():
                tgt = None
                if tx_output is None or tx_output.addresses is None or tx_output.addresses[0] is None:
                    tgt = None
                else:
                    tgt = tx_output.addresses[0]
                flow = {'src': src, 'tgt': tgt,
                        'value': tx_output.value}
                bc_flows += [flow]
        return bc_flows


class BlockChain(object):

    """
    Bitcoin block chain.
    """

    def __init__(self, bitcoin_proxy):
        """
        Creates a block chain object.

        :param BitcoinProxy bitcoin_proxy: reference to Bitcoin proxy
        :return: block chain object
        :rtype: BlockChain
        """
        self._bitcoin_proxy = bitcoin_proxy

    def get_block_by_hash(self, block_hash):
        """
        Returns a block by given block hash.

        :param str block_hash: hash of block to be returned
        :return: the requested block
        :rtype: Block
        :raises BlockchainException: if block cannot be retrieved
        """
        # Returns block by hash
        try:
            raw_block_data = self._bitcoin_proxy.getblock(block_hash)
            return Block(raw_block_data, self)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve block %s"
                                      % (block_hash), exc)

    def get_block_by_height(self, block_height):
        """
        Returns a block by given block height.

        :param str block_height: height of block to be returned
        :return: the requested block
        :rtype: Block
        :raises BlockchainException: if block cannot be retrieved
        """
        # Returns block by height
        try:
            block_hash = self._bitcoin_proxy.getblockhash(block_height)
            return self.get_block_by_hash(block_hash)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve block with height %s"
                                      % (block_height), exc)

    def get_blocks_in_range(self, start_height=0, end_height=0):
        """
        Generates blocks in a given range.

        :param int start_height: first block height in range
        :param int end_height: last block height in range
        :yield: the requested blocks
        :rtype: Block
        """
        block = self.get_block_by_height(start_height)
        while (block.height <= end_height):
            yield block
            if not block.hasnextblock:
                break
            else:
                block = block.nextblock

    def get_transaction(self, tx_id):
        """
        Returns a transaction by given transaction id.

        :param str tx_id: transaction id
        :return: the requested transaction
        :rtype: Transaction
        """
        try:
            raw_tx_data = self._bitcoin_proxy.getrawtransaction(tx_id)
            return Transaction(raw_tx_data, self)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve transaction with id %s"
                                      % (tx_id), exc)

    def get_max_blockheight(self):
        """
        Returns maximum known block height.

        :return: maximum block height
        :rtype: int
        """
        try:
            max_height = self._bitcoin_proxy.getblockcount()
            return max_height
        except JSONRPCException as exc:
            raise BlockchainException("Error when retrieving maximum\
                block height", exc)
