Bitcoingraph - A Python library for exploring the Bitcoin transaction graph.

[![Build Status](https://travis-ci.org/behas/bitcoingraph.svg?branch=master)](https://travis-ci.org/behas/bitcoingraph)

## Prerequesites

### Bitcoin Core setup and configuration

First, install the current version of Bitcoin Core (v.11.1), either from [source](https://github.com/bitcoin/bitcoin) or from a [pre-compiled executable](https://bitcoin.org/en/download).

Once installed, you'll have access to three programs: `bitcoind` (= full peer), `bitcoin-qt` (= peer with GUI), and `bitcoin-cli` (RPC command line interface). The following instructions have been tested with `bitcoind` and assume you can start and run a Bitcoin Core peer as follows:

    bitcoind -printtoconsole

Second, you must make sure that your bitcoin client accepts JSON-RPC connections by modifying the [Bitcoin Core configuration file][bc_conf] as follows:

    # server=1 tells Bitcoin-QT to accept JSON-RPC commands.
    server=1

    # You must set rpcuser and rpcpassword to secure the JSON-RPC api
    rpcuser=your_rpcuser
    rpcpassword=your_rpcpass

    # How many seconds bitcoin will wait for a complete RPC HTTP request.
    # after the HTTP connection is established.
    rpctimeout=30

    # Listen for RPC connections on this TCP port:
    rpcport=8332

Test whether the JSON-RPC interface is working by starting your Bitcoin Core peer (...waiting until it finished startup...) and using the following cURL request (with adapted username and password):

    curl --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getinfo", "params": [] }' -H 'content-type: text/plain;' http://your_rpcuser:your_rpcpass@localhost:8332/


Third, since Bitcoingraph needs to access non-wallet blockchain transactions by their ids, you need to enable the transaction index in the Bitcoin Core database. This can be achieved by adding the following property to your `bitcoin.conf`

    txindex=1

... and restarting your Bitcoin core peer as follows (rebuilding the index can take a while):

    bitcoind -reindex


Test non-wallet transaction data access by taking an arbitrary transaction id and issuing the following request using cURL:

    curl --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getrawtransaction", "params": ["110ed92f558a1e3a94976ddea5c32f030670b5c58c3cc4d857ac14d7a1547a90", 1] }' -H 'content-type: text/plain;' http://your_rpcuser:your_rpcpass@localhost:8332/


Finally, bitcoingraph also makes use of Bitcoin Core's HTTP REST interface, which is enabled using the following parameter:

    bitcoind -rest

Test it using some sample block hash

    http://localhost:8332/rest/block/000000000000000e7ad69c72afc00dc4e05fc15ae3061c47d3591d07c09f2928.json


When you reached this point, your Bitcoin Core setup is working. Terminate all running bitcoind instances and launch a new background daemon with enabled REST interface

    bitcoind -daemon -rest


### Bitcoingraph library setup

Bitcoingraph is being developed in Python 3.4. Make sure it is running on your machine:

    python --version


Now clone Bitcoingraph...

    git clone https://github.com/behas/bitcoingraph.git


...test and install the Bitcoingraph library:

    cd bitcoingraph
    pip install -r requirements.txt
    py.test
    python setup.py install


### Mac OSX specifics

Running bitcoingraph on a Mac requires coreutils to be installed

    homebrew install coreutils


## Boostrapping the underlying graph database (Neo4J)

bitcoingraph stores Bitcoin transactions as directed labelled graph in a Neo4J graph database instance. This database can be bootstrapped by loading an initial blockchain dump, performing entity computation over the entire dump as described by [Ron and Shamir](https://eprint.iacr.org/2012/584.pdf), and ingesting it into a running Neo4J instance.

### Step 1: Create transaction dump from blockchain

Bitcoingraph provides the `bcgraph-export` tool for exporting transactions in a given block range from the blockchain. The following command exports all transactions contained in block range 0 to 1000 using Neo4Js header format and separate CSV header files:

    bcgraph-export 0 1000 -u your_rpcuser -p your_rpcpass

The following CSV files are created (with separate header files):

* addresses.csv: sorted list of Bitcoin addressed
* blocks.csv: list of blocks (hash, height, timestamp)
* transactions.csv: list of transactions (hash, coinbase/non-coinbase)
* outputs.csv: list of transaction outputs (output key, id, value, script type)
* rel_block_tx.csv: relationship between blocks and transactions (block_hash, tx_hash)
* rel_input.csv: relationship between transactions and transaction outputs (tx_hash, output key)
* rel_output_address.csv: relationship between outputs and addresses (output key, address)
* rel_tx_output.csv: relationship between transactions and transaction outputs (tx_hash, output key)


### Step 2: Compute entities over transaction dump

The following command computes entities for a given blockchain data dump:

    bcgraph-compute-entities -i block_0_1000

Two additional files are created:

* entities.csv: list of entity identifiers (entity_id)
* rel_address_entity.csv: assignment of addresses to entities (address, entity_id)


### Step 3: Ingest pre-computed dump into Neo4J

Download and install [Neo4J][neo4j] community edition (>= 2.3.0):

    tar xvfz neo4j-community-2.3.0-unix.tar.gz
    export NEO4J_HOME=[PATH_TO_NEO4J_INSTALLATION]

Test Neo4J installation:

    $NEO4J_HOME/bin/neo4j start
    http://localhost:7474/


Install  and make sure is not running and pre-existing databases are removed:

    $NEO4J_HOME/bin/neo4j stop
    rm -rf $NEO4J_HOME/data/*


Switch back into the dump directory and create a new database using Neo4J's CSV importer tool:

    $NEO4J_HOME/bin/neo4j-import --into $NEO4J_HOME/data/graph.db \
    --nodes:Block blocks_header.csv,blocks.csv \
    --nodes:Transaction transactions_header.csv,transactions.csv \
    --nodes:Output outputs_header.csv,outputs.csv \
    --nodes:Address addresses_header.csv,addresses.csv \
    --nodes:Entity entities.csv \
    --relationships:CONTAINS rel_block_tx_header.csv,rel_block_tx.csv \
    --relationships:OUTPUT rel_tx_output_header.csv,rel_tx_output.csv \
    --relationships:INPUT rel_input_header.csv,rel_input.csv \
    --relationships:USES rel_output_address_header.csv,rel_output_address.csv \
    --relationships:BELONGS_TO rel_address_entity.csv


Then, start the Neo4J shell...:

    $NEO4J_HOME/bin/neo4j-shell -path $NEO4J_HOME/data

and create the following uniquness constraints:

    CREATE CONSTRAINT ON (a:Address) ASSERT a.address IS UNIQUE;

    CREATE CONSTRAINT ON (o:Output) ASSERT o.txid_n IS UNIQUE;


Finally start Neo4J

    $NEO4J_HOME/bin/neo4j start


### Step 4: Enrich transaction graph with identity information

Some bitcoin addresses have associated public identity information. Bitcoingraph provides an example script which collects information from blockchain.info.

    utils/identity_information.py

The resulting CSV file can be imported into Neo4j with the Cypher statement:

    LOAD CSV WITH HEADERS FROM "file://<PATH>/identities.csv" AS row
    MERGE (a:Address {address: row.address})
    CREATE a-[:HAS]->(i:Identity
      {name: row.tag, link: row.link, source: "https://blockchain.info/"})


### Step 5: Install Neo4J entity computation plugin

Clone the git repository and compile from source. This requires Maven and Java JDK to be installed.

    git clone https://github.com/romankarl/entity-plugin.git
    cd entity-plugin
    mvn package

Copy the JAR package into Neo4j's plugin directory.

    service neo4j-service stop
    cp target/entities-plugin-0.0.1-SNAPSHOT.jar $NEO4J_HOME/plugins/
    service neo4j-service start



### Step 6: Enable synchronization with Bitcoin block chain

Bitcoingraph provides a synchronisation script, which reads blocks from bitcoind and writes them into Neo4j. It is intended to be called by a cron job which runs daily or more frequent. For performance reasons it is no substitution for steps 1-3.

    bcgraph-synchronize -s localhost -u RPC_USER -p RPC_PASS -S localhost -U NEO4J_USER -P NEO4J_PASS --rest


## Contributors

* [Bernhard Haslhofer](mailto:bernhard.haslhofer@ait.ac.at)
* [Roman Karl](mailto:roman.karl@ait.ac.at)


## License

This library is release Open Source under the [MIT license](http://opensource.org/licenses/MIT).

[bc_core]: https://github.com/bitcoin/bitcoin "Bitcoin Core"
[bc_conf]: https://en.bitcoin.it/wiki/Running_Bitcoin#Bitcoin.conf_Configuration_File "Bitcoin Core configuration file"
[neo4j]: http://neo4j.com/ "Neo4J"
