import unittest
import logging
from tempfile import NamedTemporaryFile 

import sqlite3  #exception handling
import bitcoingraph.entitygraphgen as etg

LOGFILE  = "./testlog.log" 
LOGLVL   = "DEBUG"
SQLITEDBFILE = "./sqlitedb.db"
KEEPDATA = False
#KEEPDATA = True

class TestSQLiteDAO(unittest.TestCase):
    """ unittests for SQLiteDAO 
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
        sql = etg.SQLiteDAO(logger=cls._logger,sqlitedb=SQLITEDBFILE)
        sql.connect()
        if (not KEEPDATA): sql.drop_table("t_btc2et")
        sql.close()

        #close logger
        cls._logfile.close()
        logging.shutdown() 
    
    def test_1_create_tables(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting create_tables")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))    

        ret = sql.create_tables()
        self.assertTrue(ret == 0,"create_table() returned error: {}".format(ret))   

        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

    def test_2_insert_btc2et(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting insert_btc2et")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))
       
        ret = sql.insert_btc2et("A1",1)
        logger.debug("insert: {}".format(ret))
        self.assertTrue(ret == 0,"insert_table() returned error: {}".format(ret))

        ret = sql.insert_btc2et("A2",2)
        logger.debug("insert: {}".format(ret))
        self.assertTrue(ret == 0,"insert_table() returned error: {}".format(ret))
        
        try:
            ret = sql.insert_btc2et("A2",2)
            logger.debug("insert: {}".format(ret))
        except sqlite3.IntegrityError as e:
            logger.debug("TEST - Exception: {}".format(e.args[0]))

        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

    def test_3_get_record_by_btcaddr(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting get_record_by_btcaddr")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))
       
        record = sql.get_record_by_btcaddr("A1")
        logger.debug("record: {}".format(record))
        self.assertTrue(record[1] == "A1" and record[2] == 1,"invalid record")     
        
        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

    def test_4_inc_provenance(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting inc_provenance")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))
       
        ret = sql.inc_provenance("A1")
        self.assertTrue(ret == 0,"inc_provenance() returned error: {}".format(ret))
        record = sql.get_record_by_btcaddr("A1")
        logger.debug("record: {}".format(record))
        self.assertTrue(record[1] == "A1" and record[3] == 1,"invalid record")     
        
        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

    def test_5_update_entity(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting update_entity")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))
       
        ret = sql.update_entity("A1",2)
        self.assertTrue(ret == 0,"inc_provenance() returned error: {}".format(ret))
        record = sql.get_record_by_btcaddr("A1")
        logger.debug("record: {}".format(record))
        self.assertTrue(record[1] == "A1" and record[2] == 2,"invalid record")     
        
        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

    def test_6_get_entity_by_btcaddr(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting get_entity_by_btcaddr")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))
       
        entity = sql.get_entity_by_btcaddr("A1")
        logger.debug("entity of record A1: {}".format(entity))
        self.assertTrue(entity == 2,"invalid record")     
        
        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

    def test_7_get_btcaddrs_by_entity(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting get_btcaddrs_by_entity")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))
       
        btcaddrs = sql.get_btcaddrs_by_entity(2)
        logger.debug("btcaddrs: {}".format(btcaddrs))
        self.assertTrue(len(btcaddrs) == 2,"invalid number of records")    
                
        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

    def test_8_get_max_entity(self):
        logger = self._logger
        logger.info("TEST -------------------------------------------")
        logger.info("TEST - Starting get_max_entity")

        # create input data
        sql = etg.SQLiteDAO(logger=logger,sqlitedb=SQLITEDBFILE)
        
        ret = sql.connect()
        self.assertTrue(ret == 0,"connect() returned error: {}".format(ret))
       
        ret = sql.get_max_entity()
        logger.debug("max entity: {}".format(ret))
        self.assertTrue(ret == 2,"invalid max entity")    
                
        ret = sql.close()
        self.assertTrue(ret == 0,"close() returned error: {}".format(ret))

        

if __name__ == '__main__':
        unittest.main()
            
