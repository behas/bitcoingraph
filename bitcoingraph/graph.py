"""
Various types of graph views for the Bitcoin block chain.

"""

__author__ = ['Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)',
              'Aljosha Judmayer (judmayer@xylem-technologies.com)']
__copyright__ = 'Copyright 2015, Bernhard Haslhofer, Aljosha Judmayer'
__license__ = "MIT"


# tx_graph/et_graph specific csv header fields
TXID = "txid"
SRC = "src"
DST = "tgt"
BTC = "value"
TIMESTAMP = "timestamp"
BLOCKID = "block_height"

# etmap specific csv header fields
ENTITYID = "entity_id"
BTCADDRS = "btc_addrs"

# btcmap specific csv header field
BTCADDR = "btc_addr"

# entity graph output files
ETG     = "etg.csv"
ETMAP   = "etmap.csv"
BTCMAP  = "btcmap.csv"

# csv special chars
DELIMCHR = ';'
QUOTECHR = '|'

# ensure list is sorted, has an impact on performance
EDGESORT = True

import os
import operator 
import csv
import logging
logger = logging.getLogger("graph")

from bitcoingraph.blockchain import BlockchainException


class GraphException(Exception):
    """
    Exception raised when interacting with blockchain graph view.
    """

    def __init__(self, msg, inner_exc=None):
        self.msg = msg
        self.inner_exc = inner_exc

    def __str__(self):
        return repr(self.msg)


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

    def sort_edges(self):
        """ 
        Sorts edges according to (BLOCKID, TXID)
        This is slightly faster than useing sorted() and prioritizes 
        low BLOCKIDs which should reduce entity changes 
        """
        self._edges.sort(key = operator.itemgetter(BLOCKID, TXID))

        

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
                        edge[SRC] = bc_flow['src']
                        edge[DST] = bc_flow['tgt']
                        # Addding named edge descriptior
                        edge[TXID] = tx.id
                        edge[BTC] = bc_flow['value']
                        edge[TIMESTAMP] = tx.time
                        edge[BLOCKID] = block.height
                        yield edge
                except BlockchainException as exc:
                    raise GraphException("Transaction graph generation failed",
                                         exc)

    def _load_from_file(self, tx_graph_file):
        """
        Loads already generated transaction graph from file.
        """
        with open(tx_graph_file, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile, delimiter=DELIMCHR,
                                            quotechar=QUOTECHR,
                                            quoting=csv.QUOTE_MINIMAL)
                for edge in csv_reader:
                    yield edge

    def export_to_csv(self, start_block=None,
                      end_block=None, output_file=None, progress=None):
        """
        Exports transaction graph to CSV file directly from blockchain.
        """
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [TXID, SRC, DST,
                          BTC, TIMESTAMP, BLOCKID]
            csv_writer = csv.DictWriter(csvfile, delimiter=DELIMCHR,
                                        quotechar=QUOTECHR,
                                        fieldnames=fieldnames,
                                        quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()
            for edge in self._generate_from_blockchain(start_block, end_block):
                csv_writer.writerow(edge)
                if progress:
                    progress(edge[BLOCKID] / (end_block - start_block))


class EntityGraph(Graph):
    """
    A directed graph view on entites in the blockchain.

    Vertex = entity
    Edge = bitcoin flow between entities

    Generator for Entity Graphs from transaction graphs
    Memory intensive variant.
    """
    def __init__(self, tx_graph=None, customlogger=None):
        """
        Creates entity graph view based on transaction graph.
        """
        self._tx_graph = tx_graph
        self._etdict = dict()   # dict() with entities as key
        self._btcdict = dict()   # dict() with btc addresses as key
        if customlogger:
            self._logger = customlogger
        else:
            self._logger = logger

        super().__init__()

        return

    def _handle_tx_inputs(self, txstack):
        """
        Generates or updates entity mapping for given group of txs of same id.
        """
        self._logger.debug("Handle txstack with len: {} in memory".format(len(txstack)))

        entity_id = None   # the entity id of all btc src addresses in this tx
        entitylist = set()  # set of all entity mappings for btc src addresses in this tx
        btcaddrlist = set()  # set all btc src addresses in this tx

        for edge in txstack:
            if (len(txstack) > 1 and edge[SRC] == 'NULL'):
                # ignore coinbase transactions or 'NULL' inputs
                self._logger.debug("Found NULL/coinbase tx input. Ignoring edge: {}".fomat(edge))
                continue

            if (edge[SRC] in self._btcdict.keys()):
                entity_id = self._btcdict[edge[SRC]]
                entitylist.add(self._btcdict[edge[SRC]])

            # create set of all unique source addresses
            btcaddrlist.add(edge[SRC])

        if len(entitylist) > 0:
            # handle entity collision and add new btc src addresses
            entity_id = min(entitylist)
            for et in entitylist:
                if et != entity_id:
                    #TODO: do the change btc address entity step here
                    self._etdict[entity_id] = self._etdict[entity_id].union(self._etdict[et])
                    self._etdict[et] = None

            # change btc address entity mapping of entries already in btc->entity dict
            for btcaddr in self._etdict[entity_id]:
                self._btcdict[btcaddr] = entity_id

            # add btc addresses to entity->btc dict
            for btcaddr in btcaddrlist:
                self._etdict[entity_id].add(btcaddr)
        else:
            # generate new entity and add new btc src addresses
            entity_id = len(self._etdict)+1
            self._etdict[entity_id] = btcaddrlist

        # add Bitcoin source address to btc->entity dict
        for btcaddr in btcaddrlist:
            self._btcdict[btcaddr] = entity_id               


    def _generate_entity_mapping(self):
        """
        Generate entiy mapping from transaction graph.
        """
        txstack = list()
        txid = None
       
        #for edge in self._tx_graph.list_edges(sort_key=TXID):
        if EDGESORT: self.sort_edges()
        for edge in self._tx_graph._edges:
            # check if still the same transaction
            if (edge[TXID] != txid and txid is not None):
                self._handle_tx_inputs(txstack)
                txstack.clear()
            txid = edge[TXID]
            txstack.append(edge)
        if (len(txstack) > 0):
            self._handle_tx_inputs(txstack)
            txstack.clear()

        self._logger.info("Finished entity graph generation.")
        return 0


    def _generate_edges(self):
        """
        Generates entity graph from tranaction graph
        """
        ret = self._generate_entity_mapping()
        if ret != 0:
            self._logger.error("Failed generating entity graph")
            raise GraphException("Entity graph generation failed", exc)

        for tx_edge in self._tx_graph._edges:
            if tx_edge[SRC] in self._btcdict.keys():
                entity_src = self._btcdict[tx_edge[SRC]]
            else:
                entity_src = "0" #undefined entity 
            if tx_edge[DST] in self._btcdict.keys():
                entity_dst = self._btcdict[tx_edge[DST]]
            else:
                entity_dst = "0"
            et_edge = dict()
            et_edge[TXID] = tx_edge[TXID]
            et_edge[SRC] = str(entity_src)
            et_edge[DST] = str(entity_dst)
            et_edge[BTC] = tx_edge[BTC]
            et_edge[TIMESTAMP] = tx_edge[TIMESTAMP]
            et_edge[BLOCKID] = tx_edge[BLOCKID]
            yield et_edge


    def generate_from_tx_graph(self, tx_graph=None):
        """ 
        Populate entity graph edges
        """
        if tx_graph:
            self._tx_graph = tx_graph
        elif self._tx_graph is None:
            self._logger.error("No tx_graph given")
            raise GraphException("No tx_graph given", None)
            
        generator = self._generate_edges()
        for edge in generator:
            self.add_edge(edge)

        return 0

    def load_from_dir(self, et_graph_dir):
        """
        Generates entity graph by loading edges from CSV file.
        """
        if not os.path.isdir(et_graph_dir):
            self._logger.error("Input entity graph directory is not a directory")
            return 1

        # clear all data structures
        self._edges.clear() 
        self._etdict.clear()
        self._btcdict.clear()

        with open(et_graph_dir + "/" + ETG,'r') as etgfp:
            etgreader = csv.DictReader(etgfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for edge in etgreader:
                self.add_edge(edge)
        
        with open(et_graph_dir + "/" + ETMAP, 'r') as etmapfp:
            etmapreader = csv.DictReader(etmapfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for etmap in etmapreader:
                if etmap[BTCADDRS] == "None":
                    self._etdict[int(etmap[ENTITYID])] = None 
                else:
                    self._etdict[int(etmap[ENTITYID])] = etmap[BTCADDRS] 

        with open(et_graph_dir + "/btcmap.csv", 'r') as btcmapfp:
            btcmapreader = csv.DictReader(btcmapfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for btcmap in btcmapreader:
                self._btcdict[str(btcmap[BTCADDR])] = int(btcmap[ENTITYID])
        
        return 0

    def export_to_csv(self, output_dir):
        """
        Export entity graph data to ouptput directory
        """
        if (len(self._btcdict) == 0 or len(self._etdict) == 0 or len(self._edges) == 0):
            self._logger.error("EntityGraph not initialized")
            return 1
        
        try:
            os.makedirs(output_dir)
        except OSError as exc:
            if not os.path.isdir(output_dir):
                raise GraphException("Output direcotry is not a directory", exc)
      
        # write entity graph 
        with open(output_dir + "/" + ETG,'w') as etgfp:
            fieldnames = [ TXID, SRC, DST, BTC, TIMESTAMP, BLOCKID ]
            csv_writer = csv.DictWriter(etgfp,
                                        delimiter=DELIMCHR,
                                        quotechar=QUOTECHR,
                                        fieldnames=fieldnames,
                                        quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()
            for edge in self._edges:
                csv_writer.writerow(edge)          
        
        # write entity mapping
        with open(output_dir + "/" + ETMAP,'w') as etmapfp:
            print(ENTITYID + DELIMCHR + BTCADDRS,file=etmapfp)
            for entity in self._etdict.items():
                print(str(entity[0]) + DELIMCHR,file=etmapfp,end='')
                if (entity[1] == None):
                    print('None',file=etmapfp)
                else:
                    for btcaddr in entity[1]:
                        print(str(btcaddr) + " ",file=etmapfp,end='')
                    print('',file=etmapfp)

        # write btc mapping
        with open(output_dir + "/" + BTCMAP ,'w') as btcmapfp:
            print(BTCADDR + DELIMCHR + ENTITYID,file=btcmapfp)
            for btcaddr in self._btcdict.items():
                print(str(btcaddr[0]) + DELIMCHR + str(btcaddr[1]),file=btcmapfp)
   
        return 0


