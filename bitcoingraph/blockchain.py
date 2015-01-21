import json
import datetime as dt

from bitcoingraph.rpc import JSONRPCException


def to_json(raw_data):
    return json.dumps(raw_data, sort_keys=True,
                      indent=4, separators=(',', ': '))


def to_time(numeric_string):
    time_as_date = dt.datetime.utcfromtimestamp(int(numeric_string))
    return time_as_date.strftime('%Y-%m-%d %H:%M:%S')


class BlockchainException(Exception):

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return repr(self.msg)


class BlockchainObject(object):

    """
    Generic wrapper class for any kind of Blockchain BlockchainObject
    """

    def __init__(self, raw_data, blockchain):
        self._raw_data = raw_data
        self._blockchain = blockchain

    @property
    def time(self):
        return self._raw_data['time']

    @property
    def time_as_dt(self):
        return to_time(self.time)

    def __str__(self):
        return to_json(self._raw_data)

    def __repr__(self):
        return to_json(self._raw_data)


class Block(BlockchainObject):

    """
    Wrapper class for block chain data
    """

    def __init__(self, raw_data, blockchain):
        super().__init__(raw_data, blockchain)

    @property
    def height(self):
        return int(self._raw_data['height'])

    @property
    def hash(self):
        return self._raw_data['hash']

    @property
    def nextblockhash(self):
        return self._raw_data['nextblockhash']

    @property
    def hasnextblock(self):
        return 'nextblockhash' in self._raw_data

    @property
    def nextblock(self):
        if self.hasnextblock:
            block_hash = self.nextblockhash
            return self._blockchain.get_block_by_hash(block_hash)
        else:
            return None

    @property
    def tx_count(self):
        return len(self._raw_data['tx'])

    @property
    def tx_ids(self):
        return self._raw_data['tx']

    @property
    def transactions(self):
        for tx_id in self.tx_ids:
            yield self._blockchain.get_transaction(tx_id)


class TxInput(object):

    """Wrapper class for transaction input"""

    def __init__(self, raw_data, blockchain):
        self._raw_data = raw_data
        self._blockchain = blockchain

    @property
    def is_coinbase(self):
        return 'coinbase' in self._raw_data

    @property
    def prev_tx_hash(self):
        if self.is_coinbase:
            return None
        else:
            return self._raw_data['txid']

    @property
    def prev_tx_output_index(self):
        if self.is_coinbase:
            return None
        else:
            return self._raw_data['vout']

    @property
    def prev_tx_output(self):
        if self.is_coinbase:
            return None
        else:
            prev_tx = self._blockchain.get_transaction(self.prev_tx_hash)
            return prev_tx.outputs[self.prev_tx_output_index]

    @property
    def addresses(self):
        if self.is_coinbase:
            return None
        else:
            return self.prev_tx_output.addresses


class TxOutput(object):

    """Wrapper class for transaction output"""

    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def index(self):
        return self._raw_data['n']

    @property
    def value(self):
        return float(self._raw_data['value'])

    @property
    def addresses(self):
        scriptPubKey = self._raw_data.get('scriptPubKey')
        if scriptPubKey is not None:
            return scriptPubKey.get('addresses')
        else:
            return None


class Transaction(BlockchainObject):

    """Wrapper class for bitcoin transactions"""

    def __init__(self, raw_data, blockchain):
        super().__init__(raw_data, blockchain)

    @property
    def blocktime(self):
        return self._raw_data['blocktime']

    @property
    def id(self):
        return self._raw_data['txid']

    @property
    def vin_count(self):
        return len(self.inputs)

    @property
    def inputs(self):
        inputs = {}
        for idx, vin in enumerate(self._raw_data['vin']):
            tx_in = TxInput(vin, self._blockchain)
            inputs[idx] = tx_in
        return inputs

    @property
    def is_coinbase_tx(self):
        return self.inputs[0].is_coinbase

    @property
    def vout_count(self):
        if 'vout' in self._raw_data:
            return len(self._raw_data['vout'])
        else:
            return 0

    @property
    def outputs(self):
        outputs = {}
        for vout in self._raw_data['vout']:
            tx_out = TxOutput(vout)
            outputs[tx_out.index] = tx_out
        return outputs

    @property
    def input_addresses(self):
        txinputs = list()
        for idx, txinput in self.inputs.items():
            if self.is_coinbase_tx: 
               txinputs.append(None) 
            else:
               txinputs.append(txinput.addresses[0]) #Why is addresses a list?
        return txinputs

    @property
    def bc_flows(self):
        bc_flows = []
        src = None
        for idx, output in self.outputs.items():
            if not self.is_coinbase_tx:
                    src = self.inputs[0].addresses[0] #TODO iterate/mathc inputs to outputs or display all of them
            tgt = None
            if output.addresses is not None:
                tgt = output.addresses[0]
            flow = {'src': src, 'tgt': tgt,
                    'value': output.value}
            bc_flows += [flow]
        return bc_flows


class BlockChain(object):

    """
    A handler for accessing Bitcoin blockchain data objects.
    """

    def __init__(self, bitcoin_proxy):
        self._bitcoin_proxy = bitcoin_proxy

    def get_block_by_hash(self, block_hash):
        # Returns block by hash
        try:
            raw_block_data = self._bitcoin_proxy.getblock(block_hash)
            return Block(raw_block_data, self)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve block %s"
                                      % (block_hash), exc)

    def get_block_by_height(self, block_height):
        # Returns block by height
        try:
            block_hash = self._bitcoin_proxy.getblockhash(block_height)
            return self.get_block_by_hash(block_hash)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve block with height %s"
                                      % (block_height), exc)

    def get_blocks_in_range(self, start_height=0, end_height=0):
        # Returns blocks for a given height range
        block = self.get_block_by_height(start_height)
        while (block.height <= end_height):
            yield block
            if not block.hasnextblock:
                break
            else:
                block = block.nextblock

    def get_transaction(self, tx_id):
        # Returns transaction for a given transaction hash
        try:
            raw_tx_data = self._bitcoin_proxy.getrawtransaction(tx_id)
            return Transaction(raw_tx_data, self)
        except JSONRPCException as exc:
            raise BlockchainException("Cannot retrieve transaction with id %s"
                                      % (tx_id), exc)
