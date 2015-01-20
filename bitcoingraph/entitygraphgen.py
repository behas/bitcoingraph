#!/usr/bin/python
"""
Script for generating entity graph data out of transaction graph data

This is a first naive approach witch is very memory intensive.
The implementation assumes that the input csv is sorted according to transaction_id 
i.e. all items of one transaction (which have the same tx_id) are grouped together.

Example usage:
$ python3.4 entitygraphgen.py -l --txgcsv ../test/data/tx_graph_testdata.csv --etmapcsv etmap.csv

Make sure graph is sorted before:
$ tail -n+2 tx_graph_1_1000.csv | sort -t';' -k6,6 -n -k1 > tx_graph_1_1000.sorted 
Since the header starts non numeric it stays first so this is not required:
$ head -n1 tx_graph_1_1000.csv > header; cat header tx_graph_1_1000.sorted >> tx_graph_1_1000.sorted
"""
import argparse
import logging
import sys
import os             #os.urandom(n)
import csv            #csv parsing 
import sqlite3

# csv header fields in tx graph file
"""
TXID       = "tx_id"
BTCADDRSRC = "btcaddr_src"
BTCADDRDST = "btcaddr_dst"
BTC        = "btc"
TIMESTAMP  = "timestamp"
BLOCKID    = "block_id"
"""
TXID       = "txid"
BTCADDRSRC = "src_addr"
BTCADDRDST = "tgt_addr"
BTC        = "value"
TIMESTAMP  = "timestamp"
BLOCKID    = "block_height"
# csv header fields in et graph file
ENTITYSRC  = "entity_src"
ENTITYDST  = "entity_dst"
# csv header fields in et mapping file
ENTITYID   = "entity_id" 

# csv settings
DELIMCHR   = ';'
QUOTECHR   = '|'


# modes of operation and specific variables
INMEMORY        = 0
SQLITEDB        = 1
SQLITEDBFILE    = "./sqlitedb.db"
PGDB            = 2



class SQLiteDAO:
    """ DAO for SQLiteDB 
    Create file with
    $ sqlite3 sqlite.db
    """
    def __init__(self,logger=None, sqlitedb=SQLITEDBFILE):
        self._logger = logger
        self._sqlitedb = sqlitedb
        self._conn = None
        self._c = None
        return 
   
    def connect(self):
        self._conn = sqlite3.connect(self._sqlitedb)
        self._c = self._conn.cursor()
        return 0

    def close(self):
        self._conn.commit()
        self._conn.close()
        return 0
 
    def create_tables(self):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1 
        self._c.execute(""" 
                        CREATE TABLE IF NOT EXISTS t_btc2et(
                            id_btc2et INTEGER PRIMARY KEY ASC,
                            btcaddr TEXT UNIQUE,
                            entity INTEGER,
                            provenance INTEGER
                        );""")
        self._c.execute("""
                        CREATE INDEX IF NOT EXISTS t_btc2et_entity ON t_btc2et(entity);""")
        self._conn.commit()
        return 0

    def drop_table(self,table):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1 
        self._c.execute("""DROP TABLE IF EXISTS t_btc2et;""") #cannot use '?' operator 
        self._conn.commit()
        return 0

    def insert_btc2et(self,btcaddr,entity):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1 
        self._c.execute("""
                        INSERT INTO t_btc2et (
                                btcaddr,
                                entity,
                                provenance )
                        VALUES (
                                ?,
                                ?,
                                0 );""",(btcaddr,entity)) 
        self._conn.commit() 
        return 0

    def update_entity(self,btcaddr,entity):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1 
        self._c.execute("""
                        UPDATE t_btc2et 
                        SET entity= ?
                        WHERE btcaddr= ? ;""",(entity,btcaddr))
        self._conn.commit()
        return 0 

    def inc_provenance(self,btcaddr):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1 
        self._c.execute("""
                        UPDATE t_btc2et 
                        SET provenance = provenance + 1
                        WHERE btcaddr= ? ;""",(btcaddr,))
        self._conn.commit()
        return 0

    def get_record_by_btcaddr(self,btcaddr):     
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1 
        self._c.execute("""
                        SELECT * 
                        FROM t_btc2et
                        WHERE btcaddr=?;""",(btcaddr,))
        return self._c.fetchone()

    def get_records_by_entity(self,entity):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1
        self._c.execute("""
                        SELECT * 
                        FROM t_btc2et
                        WHERE entity=?;""",(entity,))
        return self._c.fetchall()
    
    def get_entity_by_btcaddr(self,btcaddr):
        entity = None
        return self.get_record_by_btcaddr(btcaddr)[2]

    def get_btcaddrs_by_entity(self,entity):
        btcaddrs = list()
        records = self.get_records_by_entity(entity)
        if self._logger: self._logger.debug("records: {}".format(records))
        for record in records:
            btcaddrs.append(record[1])
        return btcaddrs
   
    def get_max_entity(self):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1
        self._c.execute("""SELECT MAX(entity) FROM t_btc2et;""") #TODO return 0 if none
        return self._c.fetchone()[0]

    def get_entity_mapping(self):
        if (self._conn == None):
            if self._logger: self._logger.error("No db connection")
            return 1
        self._c.execute("""SELECT btcaddr,entity FROM t_btc2et;""")
        return self._c.fetchall()   



class CsvParsingException(Exception):
    pass

class TxInputHandlingException(Exception):
    pass



class EntityGraphGenerator:
    """
    Generator for Entity Graphs from transaction graphs
    Memory intensive variant.
    """
    def __init__(self, logger=None, mode=INMEMORY, sqlitedb=None):
        self._logger = logger    # logger or 'None' 
        self._etdict = dict()    # dict() with entities as key 
        self._btcdict = dict()   # dict() with btc addresses as key
        self._mode = mode
        self._sqlitedb = sqlitedb
        if self._mode == SQLITEDB:
            self._logger.debug("Initializie SQLiteDB")
            self._sql = SQLiteDAO(logger=self._logger,sqlitedb=SQLITEDBFILE)
            self._sql.connect()
            self._sql.create_tables()
        return  

    def sqliteclose(self):
        if self._sql: self._sql.close()
        return

    @property
    def etdict(self):
        """ Get the Entity Dict() """
        return self._etdict

    @property
    def btcdict(self):
        """ Get the Bitcoin Adresses Dict() """
        return self._btcdict



    def check_csv_is_sorted(self, txgcsv):
        """ check if csv is sorted for tx_id"""
        #TODO
        return True

    def check_csv_sanity(self, txgcsv):
        """ check unique constraintes in csv
        i.e. tx_id,btcaddr_src,btcaddr_dst,btc
        """
        #TODO   
        return True



    def handle_tx_inputs_in_memory(self, txstack):
        if self._logger: 
            self._logger.debug("Handle txstack with len: {} in memory".format(len(txstack)))
        entity          = None    # the entity of all btc src addresses in this tx
        entitylist      = list()  # list of all entity mappings for btc src addresses in this tx
        btcaddrlist     = list()  # list of all btc src addresses in this tx
        for txitem in txstack: 
            if (self._btcdict.__contains__(txitem[BTCADDRSRC])):
                entity = self._btcdict[txitem[BTCADDRSRC]]
                entitylist.append(self._btcdict[txitem[BTCADDRSRC]])
                txitem[ENTITYSRC] = entity
                if self._logger: 
                    self._logger.debug("btcaddr \"{}\" entity: {}".format(txitem[BTCADDRSRC], entity))

            # create list of all unique source addresses
            if not btcaddrlist.__contains__(txitem[BTCADDRSRC]):
                if self._logger: 
                    self._logger.debug("btcaddrlist append: {}".format(txitem[BTCADDRSRC]))
                btcaddrlist.append(txitem[BTCADDRSRC])

        if len(entitylist) > 0:
            # handle entity collision and add new btc src addresses
            entity = min(entitylist)
            for et in entitylist:
                if et != entity:
                    self._etdict[entity].extend(self._etdict[et])
                    self._etdict[et] = None 
           
            # add btc addresses to entity->btc dict
            if self._logger: self._logger.debug("btcaddrlist: {}".format(btcaddrlist))
            for btcaddr in btcaddrlist:
                if not self._etdict[entity].__contains__(btcaddr):
                    self._etdict[entity].append(btcaddr)
            # change btc address entity mapping of entries alread in btc->entity dict
            for btcaddr in self._etdict[entity]:
                self._btcdict[btcaddr] = entity             

        if (entity == None):
            # generate new entity and add new btc src addresses 
            #entity = os.urandom(ENTITYLEN).encode("hex")                     
            entity = len(self._etdict)+1
            self._etdict[entity] = btcaddrlist

        # add Bitcoin source address to btc->entity dict
        for txitem in txstack:    
            self._btcdict[txitem[BTCADDRSRC]] = entity
 
        return txstack 



    def handle_tx_inputs_in_db(self, txstack):
        if self._logger: 
            self._logger.debug("Handle txstack with len: {} in db".format(len(txstack)))
        entity     = None
        entitylist = set()
        txstackret = list()
        for txitem in txstack:
            try:
                self._sql.insert_btc2et(txitem[BTCADDRSRC],0)
            except sqlite3.IntegrityError as e:
                self._logger.debug("sqlite3 IntegrityError: {} for: {}".format(e.args[0],txitem[BTCADDRSRC]))   
                pass
            try:
                entitylist.add(self._sql.get_entity_by_btcaddr(txitem[BTCADDRSRC]))
            except sqlite3.Error as e:
                self._logger.error("sqlite3 Error appending: {}".format(e.args[0]))
                self.sqliteclose()
                return txstackret
            txstackret.append(txitem)

        try: 
            # define min entity or generate max new one if min == 0 i.e. undefined/new
            try:
                entity = min(entitylist.difference(set((0,)))) 
            except ValueError:
                entity = 0
            if (entity == 0):
                entity = self._sql.get_max_entity() + 1
            self._logger.debug("entity = {}, entitylist = {}".format(entity,entitylist))
            
            # updated entities
            for oldet in entitylist:
                if oldet != entity:
                    btcaddrs = self._sql.get_btcaddrs_by_entity(oldet) 
                    for btcaddr in btcaddrs:
                        self._sql.update_entity(btcaddr,entity)
                        
        except sqlite3.Error as e:
            self._logger.error("sqlite3 Error getting max entity: {}".format(e.args[0]))
            self.sqliteclose()
            return txstackret 

        return txstackret




    def gen_entity_mapping(self, txgcsv):
        """
        generate entiy mapping file according to 'mode'
        """
        if (self._mode == INMEMORY or self._mode == SQLITEDB):
            return self.gen_entity_mapping_of_sorted_list(txgcsv)
        elif (self._mode == PGDB):
            return self.gen_entity_mapping_of_unsorted_list(txgcv)
        else:
            if self._logger: self._logger.error("Invalid mode of operation: {}".format(self._mode))
            else:   print("Error: invalid mode of operation: {}".format(mode))
            return 1
        
    def gen_entity_mapping_of_sorted_list(self, txgcsv):
        """
        generate entiy mapping file 
        assumtion: we run on a sorted list of transactions!
        """
        if not (self.check_csv_is_sorted(txgcsv)) or not (self.check_csv_sanity(txgcsv)):
            if self._logger: self._logger.error("Input list not sorted")
            else:   print("Input list not sorted")
            return 2
            
        if not (self.check_csv_sanity(txgcsv)):
            if self._logger: self._logger.error("Input list not sain")
            else:   print("Input list not sain")
            return 3
        
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
                    if (self._mode == INMEMORY):
                        txstack = self.handle_tx_inputs_in_memory(txstack) 
                    else:
                        txstack = self.handle_tx_inputs_in_db(txstack) 
                    break 
        
                # check if still the same transaction
                if (line[TXID] != txid and txid != None):
                    # next transaction, check/map current tx inputs to entity
                    numtx = len(txstack)
                    if (self._mode == INMEMORY):
                        txstack = self.handle_tx_inputs_in_memory(txstack) 
                    else:
                        txstack = self.handle_tx_inputs_in_db(txstack)
                    if numtx != len(txstack):
                        if self._logger: 
                            self._logger.error("Error handling tx inptus: {}".format(txsack))
                        else:   
                            print("Error handling tx inptus: {}".format(txsack))
                        raise TxInputHandlingException("Tx inputs handling failed")
                        return 5
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

    def gen_entity_mapping_of_unsorted_list(self, txgcsv):
        """ 
        generate entiy mapping file
        """
        with open(txgcsv,'r') as txgfp:
            txgreader  = csv.DictReader(txgfp,delimiter=',', quotechar='\"')
            txin_btcaddrs = list()
            txin_ets      = list()
            for line in txgreader:
                txid = line[TXID]
                #TODO
        return 0




    def print_entity_mapping(self, etmapcsv):
        """ print the entity mapping as csv file
        """ 
        if (self._mode == INMEMORY):
            return self.print_entity_mapping_from_memory(etmapcsv)
        elif (self._mode == SQLITEDB):
            return self.print_entity_mapping_from_sqlitedb(etmapcsv)
        else:
            if self._logger: self._logger.error("Invalid mode of operation: {}".format(self._mode))
            else:   print("Error: invalid mode of operation: {}".format(mode))
            return 1 

    def print_entity_mapping_from_memory(self, etmapcsv):
        """ print the entity mapping csv file from dicts in memory 
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

    def print_entity_mapping_from_sqlitedb(self, etmapcsv):
        """ print the entity mapping csv file from db
        """ 
        etdict = dict()
        maxet  = self._sql.get_max_entity()
        
        with open(etmapcsv,"w") as etmapfp:
            print(ENTITYID + "," + BTCADDRSRC,file=etmapfp)
            for et in range(1,maxet+1):
                btcaddrs = self._sql.get_btcaddrs_by_entity(et)
                if (btcaddrs == None or len(btcaddrs) == 0):
                    next
                print(str(et) + ",",file=etmapfp,end='')
                for btcaddr in btcaddrs:
                    print(str(btcaddr) + " ",file=etmapfp,end='')
                print('',file=etmapfp)
        return 0 



    def print_btcaddr_mapping(self, btcmapcsv):
        """ print the btcaddr mapping as csv file
        """ 
        if (self._mode == INMEMORY):
            return self.print_btcaddr_mapping_from_memory(btcmapcsv)
        elif (self._mode == SQLITEDB):
            return self.print_btcaddr_mapping_from_sqlitedb(btcmapcsv)
        else:
            if self._logger: self._logger.error("Invalid mode of operation: {}".format(self._mode))
            else:   print("Error: invalid mode of operation: {}".format(mode))
            return 1  

    def print_btcaddr_mapping_from_memory(self,btcmapcsv):
        """ print the btcaddr mapping as csv file from dicts in memory
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

    def print_btcaddr_mapping_from_sqlitedb(self,btcmapcsv):
        """ print the btcaddr mapping as csv file form sqlitedb
        """
        with open(btcmapcsv,"w") as btcmapfp:
            print(BTCADDRSRC + "," + ENTITYID,file=btcmapfp)
            for btcaddr in self._sql.get_entity_mapping():
                print(str(btcaddr[0]) + "," + str(btcaddr[1]),file=btcmapfp)
        return 0   




    def print_entity_graph(self, etgcsv):
        """ print the entity graph csv file
        """
        if (self._mode == INMEMORY):
            return self.print_entity_graph_from_memory(etgcsv)
        elif (self._mode == SQLITEDB):
            return self.print_entity_graph_from_sqlitedb(etgcsv)
        else:
            if self._logger: self._logger.error("Invalid mode of operation: {}".format(self._mode))
            else:   print("Error: invalid mode of operation: {}".format(mode))
            return 1 

    def print_entity_graph_from_memory(self, etgcsv):
        """ print the entity graph csv file from in memory dict
        """
        with open(etgcsv,'w') as fp:
            print(TXID + ",",
                  ENTITYSRC + ",",
                  BTCADDRSRC + ",",
                  ENTITYDST + ",", 
                  BTCADDRDST + ",",
                  BTC + ",",
                  TIMESTAMP + ",",
                  BLOCKID,file=fp)
        
        # TODO
        return 0 
     
    def print_entity_graph_from_sqlitedb(self, etgcsv):
        """ print the entity graph file from sqlitedb
        """
        # TODO
        return 0 



# ---------------------------------------------------------------------------------


def handle_arguments(args):
    arguments = args

    parser = argparse.ArgumentParser(description='Bitcoin entity graph generator')
    parser.add_argument('-l',
                    action='store_true',
                    default = False,
                    dest='logging',
                    help='Enable Logging')
    parser.add_argument('-lf',
                    action='store_true',
                    default = False,
                    dest='logfile',
                    help='Enable Logging to file, default is stdout when -l flag is given')
    parser.add_argument('-lv',
                    action='store',
                    default='DEBUG',
                    dest='loglevel',
                    help='Set the loglevel, default is DEBUG when -l flag is given')
    parser.add_argument('--txgcsv',
                    action='store',
                    default=None,
                    dest='txgcsv',
                    type=str,
                    help='The path and name to the transaction graph csv file')
    parser.add_argument('--etgcsv',
                    action='store',
                    default='./entity_graph.csv',
                    dest='etgcsv',
                    type=str,
                    help='The path and name to the entity graph csv file')
    parser.add_argument('--etmapcsv',
                    action='store',
                    default='./entity_map.csv',
                    dest='etmapcsv',
                    type=str,
                    help='The path and name to the entity mapping csv file.') 
    parser.add_argument('--btcmapcsv',
                    action='store',
                    default='./btc_map.csv',
                    dest='btcmapcsv',
                    type=str,
                    help='The path and name to the btcaddr mapping csv file.')  
    parser.add_argument('--sqlitedb',
                    action='store',
                    default=None,
                    dest='sqlitedb',
                    type=str,
                    help='The path and name to the sqlite db file')  
    arguments = parser.parse_args()
    return arguments 


def setup_logger(args,log):
    logger = log
    arguments = args

    if arguments.logging:
        # Set log message format
        #formatter = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
        #formatter = logging.Formatter( '%(asctime)s - %(levelname)s - %(message)s' )
        formatter = logging.Formatter( '%(levelname)s - %(message)s' )
       
        # Set loglevel
        numeric_level = getattr(logging, arguments.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            print("Invalid log level: {}, defaulting to 'DEBUG'".format(arguments.loglevel,))
            numeric_level = getattr(logging, "DEBUG", None)
        logger = logging.getLogger( "l" ) # some name for logger
        logger.setLevel(level=numeric_level)

        if arguments.logfile:
            # create RotatingFile handler with max 10 logFiles with max 100MB each
            rf = logging.handlers.RotatingFileHandler( arguments.logfile, maxBytes=104857600, backupCount=10 )
            rf.setLevel( numeric_level )
            rf.setFormatter( formatter )
            logger.addHandler( rf )
        else:
            # create stdout stream handler
            ch = logging.StreamHandler()
            ch.setLevel( numeric_level )
            ch.setFormatter( formatter )
            logger.addHandler( ch )
        logger.debug('Configured logger for loglevel: {}'.format(numeric_level))
    return logger 


def main():
    arguments = None  # arguments storage
    logger    = None  # logger 

    arguments = handle_arguments(arguments)
    logger = setup_logger(arguments, logger)    

    if (arguments.etgcsv):
        etgcsv = str(arguments.etgcsv)    
    if logger: logger.info("Entity graph output file: {}".format(etgcsv))
    else: print("Entity graph output file: {}".format(etgcsv))
    
    if (arguments.etmapcsv):
        etmapcsv = str(arguments.etmapcsv)    
    if logger: logger.info("Entity mapping output file: {}".format(etmapcsv))
    else: print("Entity mapping output file: {}".format(etmapcsv))

    if (arguments.btcmapcsv):
        btcmapcsv = str(arguments.btcmapcsv)    
    if logger: logger.info("Bitcon address mapping output file: {}".format(btcmapcsv))
    else: print("Bitcoin address mapping output file: {}".format(btcmapcsv))

    if (arguments.txgcsv):
        txgcsv = str(arguments.txgcsv)
        if logger: logger.info("Tx graph file {}\nStarting ...".format(txgcsv))
        else:   print("Tx graph file {}\nStarting ...".format(txgcsv))
        if (arguments.sqlitedb):
            etgenerator = EntityGraphGenerator(logger=logger,mode=SQLITEDB,sqlitedb=str(arguments.sqlitedb))
        else:    
            etgenerator = EntityGraphGenerator(logger=logger)
        etgenerator.gen_entity_mapping(txgcsv)
        etgenerator.print_entity_mapping(etmapcsv)
        etgenerator.print_btcaddr_mapping(btcmapcsv)
        if (arguments.sqlitedb):
            etgenerator.sqliteclose()
    else:
        if logger: logger.error("No input transaction graph csv given. Aporting")
        else:   print("No input transaction graph csv given. Aporting")

    return 0

if __name__ == "__main__":
    sys.exit(main())

