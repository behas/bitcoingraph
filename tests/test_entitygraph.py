import unittest
import logging
from tempfile import NamedTemporaryFile 

from bitcoingraph.graph import *

LOG = True
LOGFILE = "/tmp/testlog.log" 
LOGLVL = "DEBUG"

EXPORTDIR = "/tmp/etdata"

class TestEntityGraph(unittest.TestCase):
    """ 
    unittests for EnitityGraph class
    $ rm /tmp/testlog.log; python3.4 test/test_entitygraph.py
    """

    @classmethod
    def setUpClass(cls):
        """ 
        config logging if available and initialize edges 
        """
        if LOG:
            formatter = logging.Formatter( '%(levelname)s \t- %(message)s' )
            numeric_level = getattr(logging, LOGLVL , None) 
            cls._logger = logging.getLogger("test")
            cls._logger.setLevel(level=numeric_level)

            cls._logfile = logging.FileHandler( LOGFILE,mode='a',encoding=None,delay=False)
            cls._logfile.setLevel( numeric_level )
            cls._logfile.setFormatter( formatter )
            cls._logger.addHandler( cls._logfile )
        
        """
        # create input data inline file
        inlinefile = '''txid;src_addr;tgt_addr;value;timestamp;block_height
1111;A1;XX;0.1;1417611696;111
1111;A2;XX;0.1;1417611696;111
1111;A2;XX;0.1;1417611696;111
2222;B1;XX;0.1;1417611696;111
2222;B2;XX;0.1;1417611696;111
2222;B1;XX;0.1;1417611696;111
2222;B2;XX;0.1;1417611696;111
2222;B1;XX;0.1;1417611696;111
2222;B3;XX;0.1;1417611696;111
3333;C1;XX;0.1;1417611696;111
4444;A3;XX;0.1;1417611696;111
4444;A4;XX;0.1;1417611696;111
4444;A4;XX;0.1;1417611696;111
4444;A1;XX;0.1;1417611696;111
5555;C1;XX;0.1;1417611696;111
5555;C2;XX;0.1;1417611696;111
6666;B4;XX;0.1;1417611696;111
6666;C2;XX;0.1;1417611696;111
6666;B3;XX;0.1;1417611696;111
7777;D1;XX;0.1;1417611696;111
8888;A1;XX;0.1;1417611696;111
8888;D1;XX;0.1;1417611696;111
9999;E1;XX;0.1;1417611696;111
9999;E2;XX;0.1;1417611696;111
aaaa;F1;XX;0.1;1417611696;111
aaaa;F2;XX;0.1;1417611696;111
bbbb;F1;XX;0.1;1417611696;111
bbbb;C2;XX;0.1;1417611696;111
'''
        with NamedTemporaryFile(mode='w+',delete=False) as infile:
            print(inlinefile,file=infile,end='') 
        logger.debug("TEST - Tempfile: {}".format(infile.name))
        """
        cls._edges = list()
        
        cls._edges.append({ TXID : "1111", SRC : "A1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "1111", SRC : "A2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "1111", SRC : "A2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        
        cls._edges.append({ TXID : "2222", SRC : "B1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "2222", SRC : "B2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "2222", SRC : "B1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "2222", SRC : "B2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "2222", SRC : "B1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "2222", SRC : "B3" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
    
        cls._edges.append({ TXID : "3333", SRC : "C1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        
        cls._edges.append({ TXID : "4444", SRC : "A3" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "4444", SRC : "A4" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "4444", SRC : "A4" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "4444", SRC : "A1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" }) #union

        cls._edges.append({ TXID : "5555", SRC : "C1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" }) #union
        cls._edges.append({ TXID : "5555", SRC : "C2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
       
        cls._edges.append({ TXID : "6666", SRC : "B4" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "6666", SRC : "C2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" }) #union
        cls._edges.append({ TXID : "6666", SRC : "B3" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })

        cls._edges.append({ TXID : "7777", SRC : "D1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })

        cls._edges.append({ TXID : "8888", SRC : "A1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" }) #union
        cls._edges.append({ TXID : "8888", SRC : "D1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" }) 
   
        cls._edges.append({ TXID : "9999", SRC : "E1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "9999", SRC : "E2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })

        cls._edges.append({ TXID : "aaaa", SRC : "F1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
        cls._edges.append({ TXID : "aaaa", SRC : "F2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
 
        cls._edges.append({ TXID : "bbbb", SRC : "F1" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" }) #union
        cls._edges.append({ TXID : "bbbb", SRC : "C2" , DST : "XX" , BTC : "0", TIMESTAMP : "0", BLOCKID : "0" })
       
    @classmethod
    def tearDownClass(cls):
        """
        close logger if available and delete edges
        """
        if LOG:
            cls._logfile.close()
            logging.shutdown() 
            del cls._logfile
            del cls._logger

        del cls._edges
        
    def test_generate_entity_mapping(self):
        """ join input BTC adresses of multiple tx """
        if LOG:
            logger = self._logger
            logger.info("TEST -------------------------------------------")
            logger.info("TEST - Starting test_generate_entity_mapping")
                   
        tx_graph = TransactionGraph(None)
        tx_graph._edges=self._edges   

        etg = EntityGraph(tx_graph=tx_graph, customlogger=logger)
        ret = etg.generate_from_tx_graph(tx_graph)
        
        self.assertTrue(ret == 0,"Entity mapping method returned an error: {}".format(ret))                
        
        # test entity mapping  
        if LOG: logger.debug("TEST - Entity Dict: {}".format(etg._etdict)) 
        self.assertTrue(etg._etdict.__contains__(1),"etdict hast no key 1")
        self.assertTrue(etg._etdict.get(1).__contains__("A1"),"invalid mapping")
        self.assertTrue(etg._etdict.get(1).__contains__("A2"),"invalid mapping")
        self.assertTrue(etg._etdict.get(1).__contains__("A3"),"invalid mapping")
        self.assertTrue(etg._etdict.get(1).__contains__("A4"),"invalid mapping")
        
        self.assertTrue(etg._etdict.__contains__(2),"etdict hast no key 2")
        self.assertTrue(etg._etdict.get(2).__contains__("B1"),"invalid mapping") 
        self.assertTrue(etg._etdict.get(2).__contains__("B2"),"invalid mapping") 
        self.assertTrue(etg._etdict.get(2).__contains__("B3"),"invalid mapping") 
        self.assertTrue(etg._etdict.get(2).__contains__("B4"),"invalid mapping") 
        
        self.assertTrue(etg._etdict.__contains__(3),"etdict has no key 3")
        self.assertTrue(etg._etdict.get(3) == None, "invalid mapping")
        self.assertTrue(etg._etdict.get(2).__contains__("C1"),"invalid mapping") 
        self.assertTrue(etg._etdict.get(2).__contains__("C2"),"invalid mapping") 
       
        self.assertTrue(etg._etdict.__contains__(4),"etdict has no key 4")
        self.assertTrue(etg._etdict.get(4) == None, "invalid mapping")
        self.assertTrue(etg._etdict.get(1).__contains__("D1"),"invalid mapping") 
 
        self.assertTrue(etg._etdict.__contains__(5),"etdict has no key 4")
        self.assertTrue(etg._etdict.get(5).__contains__("E1"),"invalid mapping")
        self.assertTrue(etg._etdict.get(5).__contains__("E2"),"invalid mapping") 
       
        self.assertTrue(etg._etdict.__contains__(6),"etdict has no key 4")
        self.assertTrue(etg._etdict.get(6) == None, "invalid mapping")
        self.assertTrue(etg._etdict.get(2).__contains__("F1"),"invalid mapping")
        self.assertTrue(etg._etdict.get(2).__contains__("F2"),"invalid mapping")  

        # test bitcoin address mapping
        if LOG: logger.debug("TEST - BTC Dict: {}".format(etg._btcdict))
        self.assertTrue(etg._btcdict.__contains__("A1"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("A2"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("A3"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("A4"),"BTC address not found")
        self.assertTrue(etg._btcdict.get("A1") == 1,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("A2") == 1,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("A3") == 1,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("A4") == 1,"incorrect numbering")                    
        self.assertTrue(etg._btcdict.__contains__("B1"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("B2"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("B3"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("B4"),"BTC address not found")
        self.assertTrue(etg._btcdict.get("B1") == 2,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("B2") == 2,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("B3") == 2,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("B4") == 2,"incorrect numbering")

        self.assertTrue(etg._btcdict.__contains__("C1"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("C2"),"BTC address not found")
        self.assertTrue(etg._btcdict.get("C1") == 2,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("C2") == 2,"incorrect numbering")

        self.assertTrue(etg._btcdict.__contains__("D1"),"BTC address not found")
        self.assertTrue(etg._btcdict.get("D1") == 1,"incorrect numbering")

        self.assertTrue(etg._btcdict.__contains__("E1"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("E2"),"BTC address not found")
        self.assertTrue(etg._btcdict.get("E1") == 5,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("E2") == 5,"incorrect numbering")

        self.assertTrue(etg._btcdict.__contains__("F1"),"BTC address not found")
        self.assertTrue(etg._btcdict.__contains__("F2"),"BTC address not found")
        self.assertTrue(etg._btcdict.get("F1") == 2,"incorrect numbering")
        self.assertTrue(etg._btcdict.get("F2") == 2,"incorrect numbering")
 
    def test_export_to_csv_and_load_from_file(self):
        """ join input BTC adresses of multiple tx """
        if LOG:
            logger = self._logger
            logger.info("TEST -------------------------------------------")
            logger.info("TEST - Starting test_export_to_csv_and_load_from_file")
        
        tx_graph = TransactionGraph(None)
        tx_graph._edges=self._edges   

        etg = EntityGraph(tx_graph=tx_graph, customlogger=logger)
        ret = etg.generate_from_tx_graph(tx_graph)
        
        self.assertTrue(ret == 0,"Entity mapping method returned an error: {}".format(ret))                
        
        etg.export_to_csv(EXPORTDIR) 
        
        self.assertTrue(os.path.isdir(EXPORTDIR))
        self.assertTrue(os.path.isfile(EXPORTDIR + "/" + ETG))
        self.assertTrue(os.path.isfile(EXPORTDIR + "/" + ETMAP))
        self.assertTrue(os.path.isfile(EXPORTDIR + "/" + BTCMAP))

        
        etg2 = EntityGraph(tx_graph=None, customlogger=logger)
        ret = etg2.load_from_dir(EXPORTDIR)  
        
        self.assertTrue(ret == 0,"EntityGraph loading method returned an error: {}".format(ret))                
     
        # test entity mapping  
        if LOG: logger.debug("TEST - Entity Dict: {}".format(etg2._etdict)) 
        self.assertTrue(etg2._etdict.__contains__(1),"etdict hast no key 1")
        self.assertTrue(etg2._etdict.get(1).__contains__("A1"),"invalid mapping")
        self.assertTrue(etg2._etdict.get(1).__contains__("A2"),"invalid mapping")
        self.assertTrue(etg2._etdict.get(1).__contains__("A3"),"invalid mapping")
        self.assertTrue(etg2._etdict.get(1).__contains__("A4"),"invalid mapping")
        
        self.assertTrue(etg2._etdict.__contains__(2),"etdict hast no key 2")
        self.assertTrue(etg2._etdict.get(2).__contains__("B1"),"invalid mapping") 
        self.assertTrue(etg2._etdict.get(2).__contains__("B2"),"invalid mapping") 
        self.assertTrue(etg2._etdict.get(2).__contains__("B3"),"invalid mapping") 
        self.assertTrue(etg2._etdict.get(2).__contains__("B4"),"invalid mapping") 
        
        self.assertTrue(etg2._etdict.__contains__(3),"etdict has no key 3")
        self.assertTrue(etg2._etdict.get(3) == None, "invalid mapping")
        self.assertTrue(etg2._etdict.get(2).__contains__("C1"),"invalid mapping") 
        self.assertTrue(etg2._etdict.get(2).__contains__("C2"),"invalid mapping") 
       
        self.assertTrue(etg2._etdict.__contains__(4),"etdict has no key 4")
        self.assertTrue(etg2._etdict.get(4) == None, "invalid mapping")
        self.assertTrue(etg2._etdict.get(1).__contains__("D1"),"invalid mapping") 
 
        self.assertTrue(etg2._etdict.__contains__(5),"etdict has no key 4")
        self.assertTrue(etg2._etdict.get(5).__contains__("E1"),"invalid mapping")
        self.assertTrue(etg2._etdict.get(5).__contains__("E2"),"invalid mapping") 
       
        self.assertTrue(etg2._etdict.__contains__(6),"etdict has no key 4")
        self.assertTrue(etg2._etdict.get(6) == None, "invalid mapping")
        self.assertTrue(etg2._etdict.get(2).__contains__("F1"),"invalid mapping")
        self.assertTrue(etg2._etdict.get(2).__contains__("F2"),"invalid mapping")  

        # test bitcoin address mapping
        if LOG: logger.debug("TEST - BTC Dict: {}".format(etg2._btcdict))
        self.assertTrue(etg2._btcdict.__contains__("A1"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("A2"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("A3"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("A4"),"BTC address not found")
        self.assertTrue(etg2._btcdict.get("A1") == 1,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("A2") == 1,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("A3") == 1,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("A4") == 1,"incorrect numbering")                    
        self.assertTrue(etg2._btcdict.__contains__("B1"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("B2"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("B3"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("B4"),"BTC address not found")
        self.assertTrue(etg2._btcdict.get("B1") == 2,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("B2") == 2,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("B3") == 2,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("B4") == 2,"incorrect numbering")

        self.assertTrue(etg2._btcdict.__contains__("C1"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("C2"),"BTC address not found")
        self.assertTrue(etg2._btcdict.get("C1") == 2,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("C2") == 2,"incorrect numbering")

        self.assertTrue(etg2._btcdict.__contains__("D1"),"BTC address not found")
        self.assertTrue(etg2._btcdict.get("D1") == 1,"incorrect numbering")

        self.assertTrue(etg2._btcdict.__contains__("E1"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("E2"),"BTC address not found")
        self.assertTrue(etg2._btcdict.get("E1") == 5,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("E2") == 5,"incorrect numbering")

        self.assertTrue(etg2._btcdict.__contains__("F1"),"BTC address not found")
        self.assertTrue(etg2._btcdict.__contains__("F2"),"BTC address not found")
        self.assertTrue(etg2._btcdict.get("F1") == 2,"incorrect numbering")
        self.assertTrue(etg2._btcdict.get("F2") == 2,"incorrect numbering")
 

 
        if EXPORTDIR.startswith("/tmp"):
            os.remove(EXPORTDIR + "/" + ETG)
            os.remove(EXPORTDIR + "/" + ETMAP)
            os.remove(EXPORTDIR + "/" + BTCMAP)

if __name__ == '__main__':
        unittest.main()
            
