// useful link: https://linkurio.us/crunchbase-graph-importing-data-neo4j/
// useful link: http://www.markhneedham.com/blog/2014/10/23/neo4j-cypher-avoiding-the-eager/
// useful link: http://neo4j.com/developer/guide-import-csv/#_csv_data_quality


// importing transactions

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:/home/haslhoferb/projects/bitcoingraph/data/transactions.csv" AS row

CREATE (tx:Transaction {hash: row.txid, block: toInt(row.block), ts: toInt(row.timestamp), total: toInt(row.total)});

// creating transaction index

CREATE INDEX ON :Transaction(hash);

// importing input and output addresses

CREATE CONSTRAINT ON (addr:Address) ASSERT addr.hash IS UNIQUE;

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:/home/haslhoferb/projects/bitcoingraph/data/inputs.csv" AS row
MERGE (addr:Address {hash: row.address});

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:/home/haslhoferb/projects/bitcoingraph/data/outputs.csv" AS row
MERGE (addr:Address {hash: row.address});

DROP CONSTRAINT ON (addr:Address) ASSERT addr.hash IS UNIQUE;
CREATE INDEX ON :Address(hash);

// import input relationships

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:/home/haslhoferb/projects/bitcoingraph/data/inputs.csv" AS row
MATCH (addr:Address {hash: row.address})
MATCH (tx:Transaction {hash: row.txid})
CREATE (addr)-[:INPUT {value: toInt(row.value)}]->(tx);

// import output relationships

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:/home/haslhoferb/projects/bitcoingraph/data/outputs.csv" AS row
MATCH (addr:Address {hash: row.address})
MATCH (tx:Transaction {hash: row.txid})
CREATE (tx)-[:OUTPUT {value: toInt(row.value)}]->(addr);
