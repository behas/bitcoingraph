import unittest
import logging
from tempfile import NamedTemporaryFile 

import bitcoingraph.entitygraphgen as etg

LOGFILE = "./testlog.log" 
LOGLVL  = "DEBUG"
MODE    = etg.INMEMORY

class TestEntityGraphGenerator(unittest.TestCase):
    """ unittests for EnitityGraphGenerator
    $ rm ./testlog.log; python3.4 test/test_entitygraphgenerator.py; cat ./testlog.log
    """

    @classmethod
    def setUpClass(cls):
        """ config logging """
        formatter = logging.Formatter( '%(levelname)s \t- %(message)s' )
        numeric_level = getattr(logging, LOGLVL , None) 
        cls._logger = logging.getLogger("test")
        cls._logger.setLevel(level=numeric_level)

        cls._logfile = logging.FileHandler( LOGFILE,mode='a',encoding=None,delay=False)
        cls._logfile.setLevel( numeric_level )
        cls._logfile.setFormatter( formatter )
        cls._logger.addHandler( cls._logfile )
   
    @classmethod
    def tearDownClass(cls):
        """ close logger """
        cls._logfile.close()
        logging.shutdown() 
        del cls._logfile
        del cls._logger
    
    def test_union_single_tx(self):
        """ join input BTC addresses of same tx """
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting test_single_same_tx")

        # create input data
        intext = '''txid;src_addr;tgt_addr;value;timestamp;block_height
1111;A1;XX;0.1;1417611696;111
1111;A2;XX;0.1;1417611696;111
1111;A2;XX;0.1;1417611696;111
'''
        with NamedTemporaryFile(mode='w+',delete=False) as infile:
            print(intext,file=infile,end='') 
        logger.debug("TEST - Tempfile: {}".format(infile.name))
        
        # run entity map generator 
        etgenerator = etg.EntityGraphGenerator(logger=logger,mode=MODE)
        ret = etgenerator.gen_entity_mapping(infile.name)
        self.assertTrue(ret == 0,"Entity mapping method returned an error: {}".format(ret))                
        # test entity mapping  
        logger.debug("TEST - Entity Dict: {}".format(etgenerator.etdict)) 
        self.assertTrue(etgenerator.etdict.__contains__(1),"etdict hast no key 1")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A1"),"invalid mapping")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A2"),"invalid mapping") 
        
        # test bitcoin address mapping
        logger.debug("TEST - BTC Dict: {}".format(etgenerator.btcdict))
        self.assertTrue(etgenerator.btcdict.__contains__("A1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("A2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("A1") == 1,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("A2") == 1,"incorrect numbering")        


    def test_union_unrelated_tx(self):
        """ join input BTC adresses of multiple unrelated tx """
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting test_union_unrelated_tx")

        # create input data
        intext = '''txid;src_addr;tgt_addr;value;timestamp;block_height
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
'''
        with NamedTemporaryFile(mode='w+',delete=False) as infile:
            print(intext,file=infile,end='') 
        logger.debug("TEST - Tempfile: {}".format(infile.name))
        
        # run entity map generator 
        etgenerator = etg.EntityGraphGenerator(logger=logger,mode=MODE)
        ret = etgenerator.gen_entity_mapping(infile.name)
        self.assertTrue(ret == 0,"Entity mapping method returned an error: {}".format(ret))                
        # test entity mapping  
        logger.debug("TEST - Entity Dict: {}".format(etgenerator.etdict)) 
        self.assertTrue(etgenerator.etdict.__contains__(1),"etdict hast no key 1")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A1"),"invalid mapping")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A2"),"invalid mapping")
        
        self.assertTrue(etgenerator.etdict.__contains__(2),"etdict hast no key 2")
        self.assertTrue(etgenerator.etdict.get(2).__contains__("B1"),"invalid mapping") 
        self.assertTrue(etgenerator.etdict.get(2).__contains__("B2"),"invalid mapping") 
        self.assertTrue(etgenerator.etdict.get(2).__contains__("B3"),"invalid mapping") 
        
        self.assertTrue(etgenerator.etdict.__contains__(3),"etdict hast no key 3")
        self.assertTrue(etgenerator.etdict.get(3).__contains__("C1"),"invalid mapping") 
        
        # test bitcoin address mapping
        logger.debug("TEST - BTC Dict: {}".format(etgenerator.btcdict))
        self.assertTrue(etgenerator.btcdict.__contains__("A1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("A2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("A1") == 1,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("A2") == 1,"incorrect numbering")                    
        self.assertTrue(etgenerator.btcdict.__contains__("B1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("B2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("B3"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("B1") == 2,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("B2") == 2,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("B3") == 2,"incorrect numbering")

        self.assertTrue(etgenerator.btcdict.__contains__("C1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("C1") == 3,"incorrect numbering")


    def test_union_cross_tx(self):
        """ join input BTC adresses of multiple tx """
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting test_union_cross_tx")

        # create input data
        intext = '''txid;src_addr;tgt_addr;value;timestamp;block_height
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
            print(intext,file=infile,end='') 
        logger.debug("TEST - Tempfile: {}".format(infile.name))
        
        # run entity map generator 
        etgenerator = etg.EntityGraphGenerator(logger=logger,mode=MODE)
        ret = etgenerator.gen_entity_mapping(infile.name)
        self.assertTrue(ret == 0,"Entity mapping method returned an error: {}".format(ret))                
        # test entity mapping  
        logger.debug("TEST - Entity Dict: {}".format(etgenerator.etdict)) 
        self.assertTrue(etgenerator.etdict.__contains__(1),"etdict hast no key 1")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A1"),"invalid mapping")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A2"),"invalid mapping")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A3"),"invalid mapping")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("A4"),"invalid mapping")
        
        self.assertTrue(etgenerator.etdict.__contains__(2),"etdict hast no key 2")
        self.assertTrue(etgenerator.etdict.get(2).__contains__("B1"),"invalid mapping") 
        self.assertTrue(etgenerator.etdict.get(2).__contains__("B2"),"invalid mapping") 
        self.assertTrue(etgenerator.etdict.get(2).__contains__("B3"),"invalid mapping") 
        self.assertTrue(etgenerator.etdict.get(2).__contains__("B4"),"invalid mapping") 
        
        self.assertTrue(etgenerator.etdict.__contains__(3),"etdict has no key 3")
        self.assertTrue(etgenerator.etdict.get(3) == None, "invalid mapping")
        self.assertTrue(etgenerator.etdict.get(2).__contains__("C1"),"invalid mapping") 
        self.assertTrue(etgenerator.etdict.get(2).__contains__("C2"),"invalid mapping") 
       
        self.assertTrue(etgenerator.etdict.__contains__(4),"etdict has no key 4")
        self.assertTrue(etgenerator.etdict.get(4) == None, "invalid mapping")
        self.assertTrue(etgenerator.etdict.get(1).__contains__("D1"),"invalid mapping") 
 
        self.assertTrue(etgenerator.etdict.__contains__(5),"etdict has no key 4")
        self.assertTrue(etgenerator.etdict.get(5).__contains__("E1"),"invalid mapping")
        self.assertTrue(etgenerator.etdict.get(5).__contains__("E2"),"invalid mapping") 
       
        self.assertTrue(etgenerator.etdict.__contains__(6),"etdict has no key 4")
        self.assertTrue(etgenerator.etdict.get(6) == None, "invalid mapping")
        self.assertTrue(etgenerator.etdict.get(2).__contains__("F1"),"invalid mapping")
        self.assertTrue(etgenerator.etdict.get(2).__contains__("F2"),"invalid mapping")  

        # test bitcoin address mapping
        logger.debug("TEST - BTC Dict: {}".format(etgenerator.btcdict))
        self.assertTrue(etgenerator.btcdict.__contains__("A1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("A2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("A3"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("A4"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("A1") == 1,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("A2") == 1,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("A3") == 1,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("A4") == 1,"incorrect numbering")                    
        self.assertTrue(etgenerator.btcdict.__contains__("B1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("B2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("B3"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("B4"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("B1") == 2,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("B2") == 2,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("B3") == 2,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("B4") == 2,"incorrect numbering")

        self.assertTrue(etgenerator.btcdict.__contains__("C1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("C2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("C1") == 2,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("C2") == 2,"incorrect numbering")

        self.assertTrue(etgenerator.btcdict.__contains__("D1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("D1") == 1,"incorrect numbering")

        self.assertTrue(etgenerator.btcdict.__contains__("E1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("E2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("E1") == 5,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("E2") == 5,"incorrect numbering")

        self.assertTrue(etgenerator.btcdict.__contains__("F1"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.__contains__("F2"),"BTC address not found")
        self.assertTrue(etgenerator.btcdict.get("F1") == 2,"incorrect numbering")
        self.assertTrue(etgenerator.btcdict.get("F2") == 2,"incorrect numbering")
        

if __name__ == '__main__':
        unittest.main()
            
