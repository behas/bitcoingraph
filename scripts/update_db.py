
import argparse
import csv
from bitcoingraph import graphdb
import os

NEO4J_HOST = 'localhost'
NEO4J_PORT = '7474'
NEO4J_USER = 'neo4j'
NEO4J_PASS = 'neo4jpass'
db = graphdb.GraphDB(NEO4J_HOST, NEO4J_PORT, NEO4J_USER, NEO4J_PASS)


def update_db(args):

    def load(name):
        return 'LOAD CSV WITH HEADERS FROM "file://{}/{}.csv" AS row\n'.format(args.path, name)

    cypher_statements = [
        load('blocks') +
        'CREATE (b:Block {hash: row.hash, height: toInt(row.height), timestamp: toInt(row.timestamp)})',
        load('transactions') +
        'CREATE (t:Transaction {txid: row.txid, coinbase: row.coinbase = "True"})',
        load('outputs') +
        'CREATE (o:Output {txid_n: row.txid_n, n: toInt(row.n), value: toFloat(row.value), type: row.type})',
        load('rel_block_tx') +
        'MATCH (b:Block {hash: row.hash}), (t:Transaction {txid: row.txid})'
        ' CREATE (b)-[:CONTAINS]->(t)',
        load('rel_tx_output') +
        'MATCH (t:Transaction {txid: row.txid}), (o:Output {txid_n: row.txid_n})'
        ' CREATE (t)-[:OUTPUT]->(o)',
        load('rel_input') +
        'MATCH (o:Output {txid_n: row.txid_n}), (t:Transaction {txid: row.txid})'
        ' CREATE (o)-[:INPUT]->(t)',
        load('rel_output_address') +
        'MATCH (o:Output {txid_n: row.txid_n})'
        ' MERGE (a:Address {address: row.address})'
        ' CREATE (o)-[:USES]->(a)'
    ]

    for cypher_statement in cypher_statements:
        db.query(cypher_statement, {})

    with open(os.path.join(args.path, 'blocks.csv'), 'r', newline='') as blocks_file:
        block_reader = csv.DictReader(blocks_file)
        for block in block_reader:
            db.create_entities(block['hash'])


parser = argparse.ArgumentParser(description='Update the graph database based on input csv files')
parser.add_argument('path', type=int,
                    help='Input path')

args = parser.parse_args()
update_db(args)