"""
Various types of graph views for the Bitcoin block chain.

"""

__author__ = ['Bernhard Haslhofer (bernhard.haslhofer@ait.ac.at)',
              'Aljosha Judmayer (judmayer@xylem-technologies.com)']
__copyright__ = 'Copyright 2015, Bernhard Haslhofer, Aljosha Judmayer'
__license__ = "MIT"


# graph specific csv header fields
SRC = "src"
DST = "tgt"
EDGE = "edge"

TXID = "txid"
BTC = "value"   # only et_graph
TIMESTAMP = "timestamp"
BLOCKID = "block_height"

# etmap specific csv header fields
ENTITYID = "entity_id"
BTCADDRS = "btc_addrs"

# btcmap specific csv header field
BTCADDR = "btc_addr"

# entity graph output files
ETG = "etg.csv"
ETMAP = "etmap.csv"
BTCMAP = "btcmap.csv"

# csv special chars
DELIMCHR = ';'
QUOTECHR = '|'
LISTSEP = ','

# ensure list is sorted, has an impact on performance
EDGESORT = True

import os
import csv
import operator
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
    """
    def __init__(self):
        self._edges = dict()
        self._edge_ids = list()

    def add_edge(self, edge):
        """
        Add edge to graph.
        Structure ist as follows, where "$srcX" is
        either bitcoin address or entity:
        {
          "$src1": [
                    {
                     "dst":"$dst1", "edge":"...", "txid":"...",
                     "blockid":"...", ...
                    }
                    {
                     "dst":"$dst2", "edge":"...", "txid":"...",
                     "blockid":"...", ...
                    }
                    ...
                  ]
        }
        """
        if ( not edge.get(SRC) or
             not edge.get(DST) ):
            raise GraphException("Invalid 'edge' given")

        src = edge.pop(SRC) # extract SRC from edge to use as key
        if not edge.get(EDGE):
            # if edge has not edge id (EDGE) then generate one
            edge_id = len(self._edge_ids)+1
            self._edge_ids.append(edge_id)
            edge[EDGE] = edge_id

        if self._edges.get(src):
            self._edges[src].append(edge)
        else:
            self._edges[src] = list()
            self._edges[src].append(edge)

    def count_edges(self):
        """
        Returns number of edges in graph.
        """
        l = 0
        for key in self._edges:
            l += len(self._edges[key])
        return l

    def list_edges(self):
        """
        Generator for all edges in G
        """
        for src in self._edges:
            for edge in self._edges[src]:
                edge[SRC] = src
                yield edge

    def find_edges(self, x):
        """
        Find all edges, where node x is SRC or DST
        """
        r = list()

        # search all sources
        if x in self._edges:
            for edge in self._edges.get(x):
                # NOTE: this modifies dict entries; work on copy instead
                edge[SRC] = x
                r.append(edge)

        # search all destinations
        for src in self._edges:
            for edge in self._edges[src]:
                if (edge[DST] is not None and edge[DST] == x):
                    edge[SRC] = src
                    r.append(edge)
        return r

    def find_edge(self,x):
        """
        Find first reference/edge to/from node x
        """
        edges = self.find_edges(x)
        firstx = None

        for edge in edges:
            if firstx is None or edge[TIMESTAMP] < firstx[TIMESTAMP]:
                firstx = edge

        return firstx


    def find_edges_xy(self,x,y):
        """
        Find all direct edges between x and y
        """
        r = list()
        if not self._edges.get(x):
            return r

        for edge in self._edges[x]:
            if ( edge[DST] is not None and edge[DST] == y ):
                r.append(edge)

        return r


    def find_edge_x2y(self,x,y,d):
        """
        Find at least one path between x and y of max depth d
        useing recursiv IDDFS (Iterative Deepening Depth-First Search).
        This should have a time complexity of O(b^d), where
        b is the branching-factor (outdegree) and d is the depth.

        This wrapper method is required to properly initialize 'path' list().
        """
        path = list()
        return self._find_one_x2y(x,y,d,path)

    def _find_one_x2y(self,x,y,d,path):
        if d <= 0 or not self._edges.get(x):
            return list()

        for edge in self._edges[x]:
            edge[SRC] = x
            path.append(edge)
            if (edge[DST] is not None and edge[DST] == y):
                return path.copy()
            else:
                r = self._find_one_x2y(edge[DST],y,d-1,path.copy())
                if len(r) == 0:
                    path.pop()
                    continue
                else:
                    return r
        return list()

    def find_edges_x2y(self,x,y,d):
        """
        Find all paths between x and y reachable with a max
        depth of d.
        This uses a modified IDDFS (Iterative Deepening Depth-First Search).
        """
        path = list()
        self._paths = list()
        self._find_all_x2y(x,y,d,path)
        return self._paths

    def _find_all_x2y(self,x,y,d,path):
        if d <= 0 or not self._edges.get(x):
            return

        for edge in self._edges[x]:
            edge[SRC] = x
            path.append(edge)
            if (edge[DST] is not None and edge[DST] == y):
                self._paths.append(path.copy()) # copy value of list
            else:
                self._find_all_x2y(edge[DST],y,d-1,path.copy())
            path.pop()
        return


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

    def generate_from_blockchain(self, start_block=None, end_block=None):
        """
        Generates transaction graph by extracting edges from blockchain.
        """
        for edge in self._generate(start_block, end_block):
            self.add_edge(edge)

    def load_from_file(self, tx_graph_file):
        """
        Loads already generated transaction graph from file.
        """
        with open(tx_graph_file, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile, delimiter=DELIMCHR,
                                            quotechar=QUOTECHR,
                                            quoting=csv.QUOTE_MINIMAL)
                for entry in csv_reader:
                    src_list = [src.strip()
                                for src in entry[SRC].split(LISTSEP)]
                    tgt_list = [tgt.strip()
                                for tgt in entry[DST].split(LISTSEP)]
                    for src in src_list:
                        for tgt in tgt_list:
                            edge = {}
                            edge[SRC] = src
                            edge[DST] = tgt
                            # Addding additional properties
                            edge[TXID] = entry[TXID]
                            edge[BTC] = entry[BTC]
                            edge[TIMESTAMP] = entry[TIMESTAMP]
                            edge[BLOCKID] = entry[BLOCKID]
                            self.add_edge(edge)

    def export_to_csv(self, start_block=None,
                      end_block=None, output_file=None, progress=None):
        """
        Exports transaction graph to CSV file directly from blockchain.
        """
        if start_block is None:
            start_block = 1
        if end_block is None:
            end_block = self._blockchain.get_max_blockheight()

        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [TXID, SRC, DST,
                          BTC, TIMESTAMP, BLOCKID]
            csv_writer = csv.DictWriter(csvfile, delimiter=DELIMCHR,
                                        quotechar=QUOTECHR,
                                        fieldnames=fieldnames,
                                        quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()

            for block in self._blockchain.get_blocks_in_range(start_block,
                                                              end_block):
                for tx in block.transactions:
                    try:
                        for bc_flow in tx.bc_flows:
                            # Constructing CSV fields
                            src_list = LISTSEP.join(bc_flow['src_list'])
                            tgt_list = LISTSEP.join(bc_flow['tgt_list'])
                            entry = {}
                            entry[SRC] = src_list
                            entry[DST] = tgt_list
                            # Addding additional properties
                            entry[TXID] = tx.id
                            entry[BTC] = bc_flow['value']
                            entry[TIMESTAMP] = tx.time
                            entry[BLOCKID] = block.height
                            csv_writer.writerow(entry)
                            if progress:
                                progress(entry[BLOCKID] / (end_block - start_block))
                    except BlockchainException as exc:
                        raise GraphException("Transaction graph \
                            generation failed", exc)

    def _generate(self, start_block=None, end_block=None):
        """
        Generates transaction graph edges from blockchain.
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
                        for src in bc_flow['src_list']:
                            for dst in bc_flow['tgt_list']:
                                edge = {}
                                edge[SRC] = src
                                edge[DST] = dst
                                # Addding additional properties
                                edge[TXID] = tx.id
                                edge[BTC] = bc_flow['value']
                                edge[TIMESTAMP] = tx.time
                                edge[BLOCKID] = block.height
                                yield edge
                except BlockchainException as exc:
                    raise GraphException("Transaction graph generation failed",
                                         exc)


class EntityGraph(Graph):
    """
    A directed graph view on entites in the blockchain.

    Vertex = entity
    Edge = bitcoin flow between entities

    Generator for Entity Graphs from transaction graphs
    Memory intensive variant.
    """
    def __init__(self, customlogger=None, map_all_txout=False):
        """
        Creates entity graph view based on transaction graph.
        """
        self._tx_data = list()
        self._etdict = dict()   # dict() with entities as key
        self._btcdict = dict()  # dict() with btc addresses as key
        self._txoutset = set()
        self._map_all_txout = map_all_txout # Flag for mapping all txoutputs
        if customlogger:
            self._logger = customlogger
        else:
            self._logger = logger

        super().__init__()

        return

    def sort_tx_data(self):
        """
        Sorts records according to (BLOCKID, TXID)
        This is slightly faster than useing sorted() and prioritizes
        low BLOCKIDs which should reduce entity changes
        """
        self._tx_data.sort(key = operator.itemgetter(BLOCKID, TXID))

    def _handle_tx_inputs(self, record):
        """
        Generates or updates entity mapping
        """
        self._logger.debug("Handle record of tx {} with {} inputs".format(record[TXID], len(record[SRC])))

        entity_id = None   # the entity id of all btc src addresses in this tx
        entityset = set()  # set of all entity mappings for btc src addresses in this tx
        btcaddrset = set()  # set all btc src addresses in this tx

        for addr in record[SRC]:
            if ( (addr == 'COINBASE' and len(record[SRC]) >= 1) or
                  addr == 'NULL' or addr == 'None' ):
                # ignore COINBASE in regular tx or 'NULL' inputs
                self._logger.debug("Found invalid tx input address. Ignoring input in record: {}".format(record))
                continue

            if addr in self._btcdict.keys():
                entityset.add(self._btcdict[addr])
            # create set of all unique source addresses
            btcaddrset.add(addr)

        if len(entityset) > 0:
            # handle entity collision and add new btc src addresses
            entity_id = min(entityset)
            for et in entityset:
                if et != entity_id:
                    for btcaddr in self._etdict[et]:
                        # update current btc->entity mapping
                        self._btcdict[btcaddr] = entity_id

                    # union the entity mappings which merge to one single entity
                    self._etdict[entity_id] = self._etdict[entity_id].union(self._etdict[et])
                    self._etdict[et] = None

            # add new btc addresses to entity->btc dict
            for btcaddr in btcaddrset:
                self._etdict[entity_id].add(btcaddr)
        else:
            # generate new entity and add new btc src addresses
            entity_id = len(self._etdict)+1
            self._etdict[entity_id] = btcaddrset

        # add Bitcoin source address to btc->entity dict
        for btcaddr in btcaddrset:
            self._btcdict[btcaddr] = entity_id


    def _generate_entity_mapping(self):
        """
        Generate entiy mapping from transaction graph.
        """
        txstack = list()
        txid = None

        if EDGESORT: self.sort_tx_data()

        for record in self._tx_data:
            if (record[TXID] != txid or txid is None):
                # check if new or still the same transaction
                self._handle_tx_inputs(record)
            txid = record[TXID]

        if self._map_all_txout:
            # map all remaining tx outputs which
            # have not been used as inputs
            for record in self._tx_data:
                if record[DST] not in self._btcdict():
                    entity_id = len(self._etdict)+1
                    self._etdict[entity_id]  = set([record[DST]])
                    self._btcdict[record[DST]] = entity_id

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

        for record in self._tx_data:
            entityset = set()
            entity_src = 0 # undefined entity
            entity_dst = 0
            for addr in record[SRC]:
                if addr in self._btcdict.keys():
                    entityset.add(self._btcdict[addr])
            if len(entityset) == 1:
                entity_src = entityset.pop()
            elif len(entityset) > 1:
                self._logger.error("Invalid entity mapping of record {}".format(record))

            if record[DST] in self._btcdict.keys():
                entity_dst = self._btcdict[record[DST]]
            et_edge = dict()
            et_edge[TXID] = record[TXID]
            et_edge[SRC] = str(entity_src)
            et_edge[DST] = str(entity_dst)
            et_edge[BTC] = record[BTC]
            et_edge[TIMESTAMP] = record[TIMESTAMP]
            et_edge[BLOCKID] = record[BLOCKID]
            yield et_edge


    def generate_from_tx_data(self, tx_data=None, tx_data_file=None):
        """
        Populate entity graph edges
        """
        if tx_data:
            self._tx_data = tx_data
        elif tx_data_file:
            with open(tx_data_file, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile, delimiter=DELIMCHR,
                                            quotechar=QUOTECHR,
                                            quoting=csv.QUOTE_MINIMAL)
                for entry in csv_reader:
                    src_list = [src.strip()
                                for src in entry[SRC].split(LISTSEP)]
                    tgt_list = [tgt.strip()
                                for tgt in entry[DST].split(LISTSEP)]
                    for tgt in tgt_list:
                        record = {}
                        record[SRC] = src_list
                        record[DST] = tgt
                        record[TXID] = entry[TXID]
                        record[BTC] = entry[BTC]
                        record[TIMESTAMP] = entry[TIMESTAMP]
                        record[BLOCKID] = entry[BLOCKID]
                        self._tx_data.append(record)

        elif len(self._tx_data) == 0:
            self._logger.error("No tx_data given")
            raise GraphException("No tx_data given", None)

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

        # load edges
        with open(et_graph_dir + "/" + ETG,'r') as etgfp:
            etgreader = csv.DictReader(etgfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for edge in etgreader:
                self.add_edge(edge)

        # load entity mapping dict()
        with open(et_graph_dir + "/" + ETMAP, 'r') as etmapfp:
            etmapreader = csv.DictReader(etmapfp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for etmap in etmapreader:
                if etmap[BTCADDRS] == "None":
                    self._etdict[int(etmap[ENTITYID])] = None
                else:
                    btcaddrset = set()
                    for i in str(etmap[BTCADDRS]).split(): btcaddrset.add(i)
                    self._etdict[int(etmap[ENTITYID])] = btcaddrset

        # load bitcoin address mapping dict()
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
            fieldnames = [ SRC, DST, EDGE, TXID, BTC, TIMESTAMP, BLOCKID  ]
            csv_writer = csv.DictWriter(etgfp,
                                        delimiter=DELIMCHR,
                                        quotechar=QUOTECHR,
                                        fieldnames=fieldnames,
                                        quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()
            for edge in self.list_edges():
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


