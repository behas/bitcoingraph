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

# btc map specific csv header fields
BTCDATA = "btc_data" 

# self._btc mapping specific fields
BTCET = "entity"     # current entity mapping
BTCMDATA = BTCDATA   # data reference or None
BTCMCOUNT = "mcount" # mapping counter
from collections import defaultdict 

# entity graph output files
ETG = "etg.csv"
ETMAP = "etmap.csv"
BTCMAP = "btcmap.csv"
BTCDATAMAP = "btcdatamap.csv"

# csv special chars
DELIMCHR = ';'
QUOTECHR = '|'
LISTSEP = ','

# ensure list is sorted, has an impact on performance
EDGESORT = True

import os
import sys
import csv
csv.field_size_limit(sys.maxsize) # Fixes issue with very large csv fields 

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
    def __init__(self,copydata=False,customlogger=logger):
        self._edges = dict()
        self._edge_ids = list()
        self._copydata = copydata
        self._logger = customlogger

    def add_edge(self, edge):
        """
        Add edge to graph.
        Structure ist as follows, where "$srcX" is
        either bitcoin address or entity id but allways of type str!
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
        if ( ( not edge.get(SRC) or not edge.get(DST) ) and 
             ( not edge.get(SRC) == "" or not edge.get(DST) == "" ) ):
            self._logger.error("Invalid edge: {}".format(edge))
            #raise GraphException("Invalid edge given")
            return 1

        src = edge.get(SRC) # extract SRC from edge to use as key
        if not edge.get(EDGE):
            # if edge has not edge id (EDGE) then generate one
            edge_id = len(self._edge_ids)+1
            self._edge_ids.append(edge_id)
            edge[EDGE] = edge_id

        if self._edges.get(src):
            if self._copydata:
                self._edges[src].append(edge.copy())
            else:
                self._edges[src].append(edge)
        else:
            self._edges[src] = list()
            if self._copydata:
                self._edges[src].append(edge.copy())
            else:    
                self._edges[src].append(edge)

        return 0

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
                yield edge

    def find_edges(self, x):
        """
        Find all edges, where node x is SRC or DST
        """
        r = list()

        # search all sources
        if x in self._edges:
            for edge in self._edges.get(x):
                r.append(edge)

        # search all destinations
        for src in self._edges:
            for edge in self._edges[src]:
                if (edge[DST] is not None and edge[DST] == x):
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
            if edge[SRC] == edge[DST]:
                # self reference loop detection
                continue 
            if edge[DST] == y and len(path) == 0:
                # dont list one-hop matches
                continue
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
        if x == y:
            return list()
        path = list()
        self._paths = list()    # global path storage list()
        self._maxedges = 100    # maximum number of found edges, should limit large searches
        loopset = set()         
        loopset.add(x) # to add starting node to set 
        self._find_all_x2y(x,y,d,path.copy(),loopset.copy())
        return self._paths

    def _find_all_x2y(self,x,y,d,path,loopset):
        if d <= 0 or not self._edges.get(x) or self._maxedges <= 0:
            # stop if depth reached or source not found error
            return

        #self._logger.debug("Find x={} y={} d={} len(path)={} len(loopset)={} path[last]={}".format(x,y,d,len(path),len(loopset),path[len(path)-1] if len(path) > 0 else None))
        for edge in self._edges[x]:
            if edge[SRC] == edge[DST]:
                # self reference loop detection
                continue
            if edge[DST] in loopset:
                # detect loop
                continue
            loopset.add(edge[DST])
            path.append(edge)
            if (edge[DST] is not None and edge[DST] == y):
                self._paths.append(path.copy()) # copy value of list
                self._maxedges -= 1
            else:
                self._find_all_x2y(edge[DST],y,d-1,path.copy(),loopset.copy())
            path.pop()
            loopset.remove(edge[DST])
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

        super().__init__(customlogger = logger)

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

            for idx, block in enumerate(
                self._blockchain.get_blocks_in_range(start_block, end_block)):

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
                                block_range = end_block - start_block
                                if block_range == 0:
                                    block_range = 1
                                progress(idx / block_range)
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
    def __init__(self, customlogger=None, map_all_txout=True):
        """
        Creates entity graph view based on transaction graph.
        """
        self._tx_data = list()
        self._etbtc = dict() # { entity_id: [ btcaddr,btcaddr,... ] }
        #self._btcet = dict() # { btcaddr: entity_id }
        self._btcet = defaultdict( dict ) # { btcaddr: { "entity": entity_id , "id": id or None, "mapcount": count }
        #self._etid = dict()  # { entity_id: [ btcaddr,btcaddr,... ] } # subset of btcaddresses
        self._map_all_txout = map_all_txout # Flag for mapping all txoutputs
    
        if customlogger:
            super().__init__(customlogger=customlogger)
        else:
            super().__init__()

        return

    def get_entity_info(self,et):
        if int(et) in self._etbtc.keys():
            return self._etbtc.get(int(et))
        else:
            return set() #undefined

    def get_btcaddr_info(self,addr):
        if str(addr) in self._btcet.keys():
            return self._btcet.get(str(addr))
        else:
            return dict() #undefined

    def get_btcaddr_entity(self,addr):
        if str(addr) in self._btcet.keys():
            return self._btcet.get(str(addr))[BTCET]
        else:
            return 0 #undefined

    def sort_tx_data(self):
        """
        Sorts records according to (BLOCKID, TXID)
        This is slightly faster than useing sorted() and prioritizes
        low BLOCKIDs which should reduce entity changes
        """
        self._tx_data.sort(key = operator.itemgetter(BLOCKID, TXID))
 
    def unite_entities(self,entitylist):
        """
        Unite alle given entities into the entity with the smales id
        """
        entityset = set(entitylist) # remove doublicates
        entity_id = min(entityset)
        for et in entityset:
            if not et in self._etbtc.keys():
                # skip unknown/invalid entity values
                self._logger.error("Invalid entity detected during union: {}".format(et))
                continue
            if et != entity_id:
                # update all entities dispite the minimum
                for btcaddr in self._etbtc[et]:
                    # update current btc->entity mapping
                    self._btcet[btcaddr][BTCET] = entity_id

                # union the entity mappings which merge to one single entity
                self._etbtc[entity_id] = self._etbtc[entity_id].union(self._etbtc[et])
                self._etbtc[et] = None
            """
            if ( len(self._etid) > 0  and 
                 et in self._etid.keys() ): 
                # merge entity id mapping if available 
                if not entity_id in self._etid.keys() :
                    # create empty set if new
                    self._etid[entity_id] = set()
                # union the entity id mappings to merge
                self._etid[entity_id] = self._etid[entity_id].union(self._etid[et])
                self._etid[et] = None
            """
        return entity_id

    def _handle_tx_inputs(self, record):
        """
        Generates or updates entity mapping
        """
        self._logger.debug("Handle record of tx {} with {} inputs".format(record[TXID], len(record[SRC])))

        entity_id = None   # the entity id of all btc src addresses in this tx
        entityset = set()  # set of all entity mappings for btc src addresses in this tx
        btcaddrset = set()  # set all btc src addresses in this tx

        for addr in record[SRC]:
            if ( (addr == 'COINBASE' and len(record[SRC]) > 1) or
                  addr == 'NULL' or addr == 'None' ):
                # ignore COINBASE in regular tx or 'NULL' inputs
                self._logger.debug("Found invalid tx input address. Ignoring input in record: {}".format(record))
                continue

            if addr in self._btcet.keys():
                entityset.add(self._btcet[addr][BTCET])
            # create set of all unique source addresses
            btcaddrset.add(addr)

        if len(entityset) > 0:
            # handle entity collision and add new btc src addresses
            entity_id = self.unite_entities(entityset)

            # add new btc addresses to entity->btc dict
            for btcaddr in btcaddrset:
                self._etbtc[entity_id].add(btcaddr)
        else:
            # generate new entity and add new btc src addresses
            entity_id = len(self._etbtc)+1
            self._etbtc[entity_id] = btcaddrset

        # add Bitcoin source address to btc->entity dict
        for btcaddr in btcaddrset:
            self._btcet[btcaddr][BTCET] = entity_id


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
                if record[DST] not in self._btcet.keys():
                    entity_id = len(self._etbtc)+1
                    self._etbtc[entity_id]  = set([record[DST]])
                    self._btcet[record[DST]][BTCET] = entity_id

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
                if addr in self._btcet.keys():
                    entityset.add(self._btcet[addr][BTCET])
            if len(entityset) == 1:
                entity_src = entityset.pop()
            elif len(entityset) > 1:
                self._logger.error("Invalid entity mapping of record {}".format(record))

            if record[DST] in self._btcet.keys():
                entity_dst = self._btcet[record[DST]][BTCET]
            et_edge = dict()
            et_edge[TXID] = record[TXID]
            et_edge[SRC] = str(entity_src)
            et_edge[DST] = str(entity_dst)
            et_edge[BTC] = record[BTC]
            et_edge[TIMESTAMP] = record[TIMESTAMP]
            et_edge[BLOCKID] = record[BLOCKID]
            yield et_edge


    def generate_from_tx_data(self, tx_data=None, tx_graph_file=None):
        """
        Populate entity graph edges
        """
        if tx_data:
            self._tx_data = tx_data
        elif tx_graph_file:
            self._logger.info("Generating entity graph form tx_graph_file")
            with open(tx_graph_file, newline='') as csvfile:
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
        
        self._logger.info("Generated entity graph with {} entities and {} addresses".format(len(self._etbtc),len(self._btcet)))
        return 0



    def load_from_dir(self, et_graph_dir):
        """
        Generates entity graph by loading edges from CSV file.
        """
        if not os.path.isdir(et_graph_dir):
            self._logger.error("Input entity graph directory is not a directory")
            return 1
        self._logger.info("Loading entity graph from directory {}".format(et_graph_dir))

        # clear all data structures
        self._edges.clear()
        self._etbtc.clear()
        self._btcet.clear()
        try:
            path = et_graph_dir + "/" + ETG
            self._import_etg(path)
            path = et_graph_dir + "/" + ETMAP
            self._import_etmap(path)      
            path = et_graph_dir + "/" + BTCMAP
            self._import_btcmap(path)
            path = et_graph_dir + "/" + BTCDATAMAP
            if os.path.isfile(path):
                self.import_btcdatamap(path)
        except:
            e = sys.exc_info()[0]
            self._logger.error("Error importing data: {}".format(e))
            raise 

        self._logger.info("Loaded entiy graph with {} entities and {} addresses".format(len(self._etbtc),len(self._btcet)))
        return 0

    def _import_etg(self, etg_csv):
        """ import entity graph edges from csv """
        with open(etg_csv,'r') as fp:
            fr = csv.DictReader(fp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for edge in fr:
                self.add_edge(edge)

    def _import_etmap(self, etmap_csv):
        """ import entity mapping dict() """
        with open(etmap_csv, 'r') as fp:
            fr = csv.DictReader(fp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for line in fr:
                if line[BTCADDRS] == "None":
                    self._etbtc[int(line[ENTITYID])] = None
                else:
                    btcaddrset = set()
                    for i in str(line[BTCADDRS]).split(): btcaddrset.add(i)
                    self._etbtc[int(line[ENTITYID])] = btcaddrset

    def _import_btcmap(self, btcmap_csv):
        """ import bitcoin address mapping dict() """
        n = 0
        with open(btcmap_csv, 'r') as fp:
            fr = csv.DictReader(fp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for line in fr:
                self._btcet[str(line[BTCADDR])][BTCET] = int(line[ENTITYID])

    def import_btcdatamap(self, btcdatamap_csv):
        """ Import etid mapping data from csv """
        n = 0
        with open(btcdatamap_csv, 'r') as fp:
            fr = csv.DictReader(fp,delimiter=DELIMCHR, quotechar=QUOTECHR)
            for line in fr:
                if ( ( line[BTCADDR] in self._btcet.keys() ) and 
                     ( BTCDATA in line.keys() ) and 
                     ( line[BTCDATA] is not None ) ):
                        self._btcet[line[BTCADDR]][BTCDATA] = str(line[BTCDATA])
                        n += 1
        return n


    def export_to_csv(self, output_dir):
        """
        Export entity graph data to ouptput directory
        """
        if (len(self._btcet) == 0 or len(self._etbtc) == 0 or len(self._edges) == 0):
            self._logger.error("EntityGraph not initialized")
            return 1

        try:
            os.makedirs(output_dir)
        except OSError as exc:
            if not os.path.isdir(output_dir):
                raise GraphException("Output direcotry is not a directory", exc)

        self._logger.info("Exporting entity graph to directory {}".format(output_dir))

        try:
            path = output_dir + "/" + ETG
            self._export_etg(path) 
            path = output_dir + "/" + ETMAP
            self._export_etmap(path)
            path = output_dir + "/" + BTCMAP
            self._export_btcmap(path)
            path = output_dir + "/" + BTCDATAMAP
            self._export_btcdatamap(path)
        except:     
            e = sys.exc_info()[0]
            self._logger.error("Error exporting data: {}".format(e))
            raise 

        self._logger.info("Exported entity graph with {} entities and {} addresses".format(len(self._etbtc),len(self._btcet)))
        return 0

    def _export_etg(self, etg_csv):
        """ export entity graph edges to csv file """
        with open(etg_csv,'w') as fp:
           fieldnames = [ SRC, DST, EDGE, TXID, BTC, TIMESTAMP, BLOCKID  ]
           csv_writer = csv.DictWriter(fp,
                                       delimiter=DELIMCHR,
                                       quotechar=QUOTECHR,
                                       fieldnames=fieldnames,
                                       quoting=csv.QUOTE_MINIMAL)
           csv_writer.writeheader()
           for edge in self.list_edges():
               csv_writer.writerow(edge) 

    def _export_etmap(self, etmap_csv):
        """ export entity mapping to csv file """
        with open(etmap_csv, 'w') as fp:
            print(ENTITYID + DELIMCHR + BTCADDRS, file=fp)
            for entity in self._etbtc.items():
                print(str(entity[0]) + DELIMCHR, file=fp,end='')
                if (entity[1] == None):
                    print('None',file=fp)
                else:
                    for btcaddr in entity[1]:
                        print(str(btcaddr) + " ", file=fp, end='')
                    print('',file=fp)

    def _export_btcmap(self, btcmap_csv):
        """ export btcaddr mapping to csv file """
        with open(btcmap_csv,'w') as fp:
            print(BTCADDR + DELIMCHR + ENTITYID, file=fp)
            for btcaddr in self._btcet.items():
                #print(str(btcaddr[0]) + DELIMCHR + 
                #      str(btcaddr[1][BTCET]) + DELIMCHR +
                #      str(btcaddr[1][BTCDATA]),file=btcmapfp)
                print(str(btcaddr[0]) + DELIMCHR + 
                      str(btcaddr[1][BTCET]),file=fp)

    def _export_btcdatamap(self, btcdatamap_csv):
        """ export BTCDATA mapping to csv file """
        with open(btcdatamap_csv, 'w') as fp:
            print(BTCADDR + DELIMCHR + BTCDATA, file=fp)
            for btcaddr in self._btcet.items():
                if ( BTCDATA in btcaddr[1].keys() and
                     btcaddr[1][BTCDATA] is not None ) :
                    # if there is a BTCDATA set, export btcaddr
                    print(str(btcaddr[0]) + DELIMCHR + str(btcaddr[1][BTCDATA]),file=fp)
