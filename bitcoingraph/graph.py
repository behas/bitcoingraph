"""
Various types of graph views for the Bitcoin block chain.

"""

__author__ = ['Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)',
              'Aljosha Judmayer (judmayer@xylem-technologies.com)']
__copyright__ = 'Copyright 2015, Bernhard Haslhofer, Aljosha Judmayer'
__license__ = "MIT"

# csv header fields in tx graph file
TXID = "txid"
BTCADDRSRC = "src_addr"
BTCADDRDST = "tgt_addr"
BTC = "value"
TIMESTAMP = "timestamp"
BLOCKID = "block_height"
# csv header fields in et graph file
ENTITYSRC = "entity_src"
ENTITYDST = "entity_dst"
# csv header fields in et mapping file
ENTITYID = "entity_id"
# csv special chars
DELIMCHR = ';'
QUOTECHR = '|'

import csv
import logging
logger = logging.getLogger("graph")

from bitcoingraph.blockchain import BlockchainException


class GraphException(Exception):
    """
    Exception raised when interacting with blockchain graph view.
    """

    def __init__(self, msg, inner_exc):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return repr(self.msg)


class CsvParsingException(Exception):
    # TOOD: remove; just throw GraphException saying that you cannot
    # read file
    pass


class Graph(object):
    """
    A generic directed graph representation.

    TODO: wrap third party library
    TODO: implement required graph search algorithms
    """
    def __init__(self):
        self._edges = []

    def add_edge(self, edge):
        """
        Add edge to graph.
        """
        self._edges.append(edge)

    def count_edges(self):
        """
        Returns number of edges in graph.
        """
        return len(self._edges)

    def list_edges(self, sort_key=None):
        """
        Returns an optionally sorted (by sort_key) iterator overall edges.
        """
        edge_list = self._edges
        if sort_key is not None:
            edge_list = sorted(self._edges, key=lambda k: k[sort_key])
        for edge in edge_list:
            yield edge


class TransactionGraph(Graph):
    """
    A directed graph view on block chain transactions.

    Vertex = public key address (wallets)
    Edge = bitcoin flow from source to target address
    """

    def __init__(self, blockchain=None):
        """
        Creates transaction graph view on blockchain.
        """
        if blockchain is not None:
            self._blockchain = blockchain
        super().__init__()

    def load(self, start_block, end_block, tx_graph_file=None):
        """
        Loads transaction graph from blockchain or from transaction
        graph output file, if given.
        """
        if tx_graph_file:
            generator = self._load_from_file(tx_graph_file)
        else:
            generator = self._generate_from_blockchain(start_block, end_block)

        for edge in generator:
            self.add_edge(edge)

    def _generate_from_blockchain(self, start_block=None, end_block=None):
        """
        Generates transaction graph by extracting edges from blockchain.
        """
        if self._blockchain is None:
            raise GraphException("Cannot generated transaction graph without \
                reference to underlying blockchain")

        if start_block is None:
            start_block = 1
        if end_block is None:
            end_block = self._blockchain.get_max_blockheight()

        for block in self._blockchain.get_blocks_in_range(start_block,
                                                          end_block):
            for tx in block.transactions:
                try:
                    for bc_flow in tx.bc_flows:
                        # Construction transaction graph edge
                        edge = {}
                        edge['src'] = bc_flow['src']
                        edge['tgt'] = bc_flow['tgt']
                        # Addding named edge descriptior
                        edge['txid'] = tx.id
                        edge['value'] = bc_flow['value']
                        edge['timestamp'] = tx.time
                        edge['blockheight'] = block.height
                        yield edge
                except BlockchainException as exc:
                    raise GraphException("Transaction graph generation failed",
                                         exc)

    def _load_from_file(self, tx_graph_file):
        """
        Loads already generated transaction graph from file.
        """
        with open(tx_graph_file, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile, delimiter=';',
                                            quotechar='|',
                                            quoting=csv.QUOTE_MINIMAL)
                for edge in csv_reader:
                    yield edge

    def export_to_csv(self, start_block=None,
                      end_block=None, output_file=None, progress=None):
        """
        Exports transaction graph to CSV file directly from blockchain.
        """
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['txid', 'src', 'tgt',
                          'value', 'timestamp', 'blockheight']
            csv_writer = csv.DictWriter(csvfile, delimiter=';', quotechar='|',
                                        fieldnames=fieldnames,
                                        quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()
            for edge in self._generate_from_blockchain(start_block, end_block):
                csv_writer.writerow(edge)
                if progress:
                    progress(edge['blockheight'] / (end_block - start_block))


class EntityGraph(Graph):
    """
    A directed graph view on entites in the blockchain.

    Vertex = entity
    Edge = bitcoin flow between entities

    Generator for Entity Graphs from transaction graphs
    Memory intensive variant.
    """
    def __init__(self, logger=None):
        """
        Creates entity graph view based on transaction graph.
        """
        self._logger  = logger
        self._etdict  = dict()   # dict() with entities as key
        self._btcdict = dict()   # dict() with btc addresses as key

        super().__init__()

        return

    @property
    def etdict(self):
        # TODO: remove; shouldn't be accessed from outside anyway
        """ Get the Entity Dict() """
        return self._etdict

    @property
    def btcdict(self):
        # TODO: remove; shouldn't be accessed from outside anyway
        """ Get the Bitcoin Adresses Dict() """
        return self._btcdict

    def _check_csv_is_sorted(self, txgcsv):
        # TODO: remove; assume TransactionGraph takes care of sorting
        """ check if csv is sorted for txid"""
        return True

    def _handle_tx_inputs(self, txstack):
        if self._logger:
            self._logger.debug("Handle txstack with len: {} in memory".format(len(txstack)))
        entity          = None   # the entity of all btc src addresses in this tx
        entitylist      = set()  # set of all entity mappings for btc src addresses in this tx
        btcaddrlist     = set()  # set all btc src addresses in this tx
        rtxstack        = list() # return list

        for txitem in txstack:
            if (len(txstack) > 1 and txitem[BTCADDRSRC] == 'NULL'):
                # ignore coinbase transactions or 'NULL' inputs
                if self._logger: self._logger.debug("Found NULL/coinbase tx input: {}".format(txitem))
                continue

            if (self._btcdict.__contains__(txitem[BTCADDRSRC])):
                entity = self._btcdict[txitem[BTCADDRSRC]]
                entitylist.add(self._btcdict[txitem[BTCADDRSRC]])
                txitem[ENTITYSRC] = entity
                if self._logger:
                    self._logger.debug("btcaddr \"{}\" entity: {}".format(txitem[BTCADDRSRC], entity))

            # create set of all unique source addresses
            btcaddrlist.add(txitem[BTCADDRSRC])
            # everythin is fine then add item to return txstack
            rtxstack.append(txitem)

        if len(entitylist) > 0:
            # handle entity collision and add new btc src addresses
            entity = min(entitylist)
            for et in entitylist:
                if et != entity:
                    self._etdict[entity] = self._etdict[entity].union(self._etdict[et])
                    self._etdict[et] = None

            # add btc addresses to entity->btc dict
            if self._logger: self._logger.debug("btcaddrlist: {}".format(btcaddrlist))
            for btcaddr in btcaddrlist:
                self._etdict[entity].add(btcaddr)
            # change btc address entity mapping of entries alread in btc->entity dict
            for btcaddr in self._etdict[entity]:
                self._btcdict[btcaddr] = entity

        if (entity == None):
            # generate new entity and add new btc src addresses
            #entity = os.urandom(ENTITYLEN).encode("hex")
            entity = len(self._etdict)+1
            self._etdict[entity] = btcaddrlist

        # add Bitcoin source address to btc->entity dict
        for txitem in rtxstack:
            self._btcdict[txitem[BTCADDRSRC]] = entity

        return rtxstack

    def load(self, tx_graph_file, et_graph_file=None):
        """
        Loads entity graph from
            * transaction graph csv file
            * entity graph csv file
        """
        if et_graph_file:
            generator = self._generate_from_file(et_graph_file)
        else:
            generator = self._generate_from_tx_graph(tx_graph_file)

        for edge in generator:
            self.add_edge(edge)

    def _generate_from_file(self, et_graph_file):
        """
        Generates entity graph by loading edges from CSV file.
        """
        with open(et_graph_file,'r') as etgfp:
            etgreader = csv.DictReader(txgfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for edge in etgreader:
                yield edge
        pass

    def _generate_from_tx_graph(self, tx_graph_file):
        """
        Generates entity graph from tranaction graph
        """
        ret = self._generate_entity_mapping(tx_graph_file)
        if ret != 0:
            if self._logger: self._logger.error("Failed generating entity graph")
            else:   print("Failed generating entity graph")
            raise GraphException("Entity graph generation failed", exc)

        with open(tx_graph_file,'r') as txgfp:
                txgreader = csv.DictReader(txgfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
                for row in txgreader:
                    if self._btcdict.__contains__(row[BTCADDRSRC]):
                        entity_src = self._btcdict[row[BTCADDRSRC]]
                    else:
                        entity_src = "NULL"
                    if self._btcdict.__contains__(row[BTCADDRDST]):
                        entity_dst = self._btcdict[row[BTCADDRDST]]
                    else:
                        entity_dst = "NULL"
                    edge = dict()
                    edge[TXID]       = row[TXID]
                    edge[ENTITYSRC]  = str(entity_src)
                    edge[BTCADDRSRC] = row[BTCADDRSRC]
                    edge[ENTITYDST]  = str(entity_dst)
                    edge[BTCADDRDST] = row[BTCADDRDST]
                    edge[BTC]        = row[BTC]
                    edge[TIMESTAMP]  = row[TIMESTAMP]
                    edge[BLOCKID]    = row[BLOCKID]
                    yield edge

    def _generate_entity_mapping(self, txgcsv):
        """
        Generate entiy mapping
        !Assumtion!: we run on a sorted list of transactions!
        """
        if not (self._check_csv_is_sorted(txgcsv)):
            if self._logger: self._logger.error("Input list not sorted")
            else:   print("Input list not sorted")
            return 2

        with open(txgcsv,'r') as txgfp:
            txgreader = csv.DictReader(txgfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            txstack   = list()
            txid      = None
            while True:
                try:
                    line = next(txgreader)
                except StopIteration:
                    if self._logger: self._logger.info("Finished reading file")
                    else:   print("Finished reading file")
                    # handle last tx
                    txstack = self._handle_tx_inputs(txstack)
                    break

                # check if still the same transaction
                if (line[TXID] != txid and txid != None):
                    # next transaction, check/map current tx inputs to entity
                    numtx = len(txstack)
                    txstack = self._handle_tx_inputs(txstack)
                    if (numtx != len(txstack)) and (len(txstack) > 0):
                        if self._logger:
                            self._logger.error("Handling tx inptus of txid={} the remaining inputs are: {}".format(txid,txstack))
                        else:
                            print("Handling tx inptus of txid={} the remaining inputs are: {}".format(txid,txstack))
                        #raise TxInputHandlingException("Tx inputs handling failed")
                        #return 5
                    while len(txstack) != 0:
                        txitem = txstack.pop()

                # store current txid, append line and go to next line/loop iteration
                txid = line[TXID]
                txstack.append(line)
                if self._logger: self._logger.debug("Processing line: {} Set tx_id: {}".format(line,txid))
                else: print("Processing line: {} Set tx_id: {}".format(line,txid))


                if (txid == None):
                    raise CsvParsingException("CSV file not well formed!")
                    return 4
        return 0



    def print_entity_mapping(self, etmapcsv):
        """ print the entity mapping as csv file
        """
        if (len(self._etdict) == 0):
            if self._logger: self._logger.error("Dict is empty")
            else:   print("Dict is empty")
            return 1

        with open(etmapcsv,"w") as etmapfp:
            print(ENTITYID + "," + BTCADDRSRC,file=etmapfp)
            for entity in self._etdict.items():
                print(str(entity[0]) + ",",file=etmapfp,end='')
                if (entity[1] == None):
                    print('None',file=etmapfp)
                else:
                    for btcaddr in entity[1]:
                        print(str(btcaddr) + " ",file=etmapfp,end='')
                    print('',file=etmapfp)

        return 0



    def print_btcaddr_mapping(self, btcmapcsv):
        """ print the btcaddr mapping as csv file
        """
        if (len(self._btcdict) == 0):
            if self._logger: self._logger.error("Dict is empty")
            else:   print("Dict is empty")
            return 1

        with open(btcmapcsv,"w") as btcmapfp:
            print(BTCADDRSRC + "," + ENTITYID,file=btcmapfp)
            for btcaddr in self._btcdict.items():
                print(str(btcaddr[0]) + "," + str(btcaddr[1]),file=btcmapfp)
        return 0


    def export_to_csv(self, tx_graph_file, output_file=None):
        """
        Exports entity graph to CSV file directly from transaction graph
        """
        with open(tx_graph_file,'r') as txgfp:
            with open(output_file,'w') as etgfp:
                fieldnames = [TXID, ENTITYSRC, BTCADDRSRC, ENTITYDST,
                              BTCADDRDST, BTC, TIMESTAMP, BLOCKID]
                csv_writer = csv.DictWriter(etgfp,
                                            delimiter=DELIMCHR,
                                            quotechar=QUOTECHR,
                                            fieldnames=fieldnames,
                                            quoting=csv.QUOTE_MINIMAL)
                csv_writer.writeheader()
                for edge in self._generate_from_tx_graph(tx_graph_file):
                    csv_writer.writerow(edge)
        return 0

