#!/usr/bin/python3.4
import argparse
import logging
import sys
import os             #os.urandom(n)
import csv            #csv parsing 

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


class TxGraphGen(object):
    #TODO
    pass

class CsvParsingException(Exception):
    pass

class TxInputHandlingException(Exception):
    pass

class EtGraphGen(object):
    """
    Generator for Entity Graphs from transaction graphs
    Memory intensive variant.
    """
    def __init__(self, logger=None):
        self._logger = logger    # logger or 'None' 
        self._etdict = dict()    # dict() with entities as key 
        self._btcdict = dict()   # dict() with btc addresses as key
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


    def handle_tx_inputs_in_memory(self, txstack):
        if self._logger: 
            self._logger.debug("Handle txstack with len: {} in memory".format(len(txstack)))
        entity          = None    # the entity of all btc src addresses in this tx
        entitylist      = set()  # list of all entity mappings for btc src addresses in this tx
        btcaddrlist     = set()  # list of all btc src addresses in this tx
        for txitem in txstack: 
            if (self._btcdict.__contains__(txitem[BTCADDRSRC])):
                entity = self._btcdict[txitem[BTCADDRSRC]]
                entitylist.add(self._btcdict[txitem[BTCADDRSRC]])
                txitem[ENTITYSRC] = entity
                if self._logger: 
                    self._logger.debug("btcaddr \"{}\" entity: {}".format(txitem[BTCADDRSRC], entity))

            # create set of all unique source addresses
            btcaddrlist.add(txitem[BTCADDRSRC])

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
        for txitem in txstack:    
            self._btcdict[txitem[BTCADDRSRC]] = entity
 
        return txstack 



    def gen_entity_mapping(self, txgcsv):
        """
        generate entiy mapping file 
        assumtion: we run on a sorted list of transactions!
        """
        if not (self.check_csv_is_sorted(txgcsv)):
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
                    txstack = self.handle_tx_inputs_in_memory(txstack) 
                    break 
        
                # check if still the same transaction
                if (line[TXID] != txid and txid != None):
                    # next transaction, check/map current tx inputs to entity
                    numtx = len(txstack)
                    txstack = self.handle_tx_inputs_in_memory(txstack) 
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



    def print_entity_graph(self, etgcsv, txgcsv):
        """ print the entity graph csv file
        """
        with open(txgcsv,'r') as txgfp:
            with open(etgcsv,'w') as etgfp:
                print(TXID          + DELIMCHR,
                      ENTITYSRC     + DELIMCHR,
                      BTCADDRSRC    + DELIMCHR,
                      ENTITYDST     + DELIMCHR, 
                      BTCADDRDST    + DELIMCHR,
                      BTC           + DELIMCHR,
                      TIMESTAMP     + DELIMCHR,
                      BLOCKID,file=etgfp)
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
                    print(row[TXID]         + DELIMCHR,
                          str(entity_src)   + DELIMCHR,
                          row[BTCADDRSRC]   + DELIMCHR,
                          str(entity_dst)   + DELIMCHR,
                          row[BTCADDRDST]   + DELIMCHR,
                          row[BTC]          + DELIMCHR,
                          row[TIMESTAMP]    + DELIMCHR,
                          row[BLOCKID],file=etgfp)
        return 0 
     
