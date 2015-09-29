Bitcoingraph - A Python library for extracting and navigating graph structures from the Bitcoin block chain.

[![Build Status](https://travis-ci.org/behas/bitcoingraph.svg?branch=develop)](https://travis-ci.org/behas/bitcoingraph)  [![Coverage Status](https://coveralls.io/repos/behas/bitcoingraph/badge.svg?branch=develop)](https://coveralls.io/r/behas/bitcoingraph?branch=develop)

# Prerequesites

## Bitcoin Core setup and configuration

First, install the current version of Bitcoin Core, either from [source](https://github.com/bitcoin/bitcoin) or from a [pre-compiled executable](https://bitcoin.org/en/download).

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

Test whether the JSON-RPC interface is working by starting your Bitcoin Core peer (...waiting until it finished startup...) and using cURL:

    curl --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getinfo", "params": [] }' -H 'content-type: text/plain;' http://your_rpcuser:your_rpcpass@localhost:8332/


Third, since Bitcoingraph needs to access non-wallet blockchain transactions by their ids, you need to enable the transaction index in the Bitcoin Core database. This can be achieved by adding the following property to your `bitcoin.conf`

    txindex=1

... and restarting your Bitcoin core peer as follows:

    bitcoind -reindex


Test non-wallet transaction data access by taking an arbitrary transaction id and issuing the following request using cURL:

    curl --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getrawtransaction", "params": ["110ed92f558a1e3a94976ddea5c32f030670b5c58c3cc4d857ac14d7a1547a90", 1] }' -H 'content-type: text/plain;' http://your_rpcuser:your_rpcpass@localhost:8332/


When you have got that far, your Bitcoin Core setup is working.

## Bitcoingraph setup

Bitcoingraph is being developed in Python 3.4. Make sure it is running on your machine:

    python --version


Now clone Bitcoingraph...

    git clone https://github.com/behas/bitcoingraph.git


...test and install the Bitcoingraph library:

    cd bitcoingraph
    pip install -r requirements.txt
    py.test
    python setup.py install



# Usage

## Blockchain export with bcgraph-export

Bitcoin graph provides the `bcgraph-export` tool for exporting transactions in a given block range from the blockchain. The following command exports all transactions contained in block range 1 to 1000.

    bcgraph-export 1 1000 -s localhost:8332 -u your_rpcuser -p your_rpcpass

Furthermore, the `-n` option can be used to write the CSV headers in Neo4J's input format.

The following files are generated in a directory called `block_1_1000`:

+ transactions.csv: data related to transactions
+ addresses.csv: all addresses that were either part of inputs or outputs (Note: list contains duplicates)
+ inputs.csv: all input relationships (Address -> Transaction)
+ outputs.csv: all output relationships (Transaction -> Address)

The address file (`addresses.csv`) contains duplicates. To deduplicate and sort the list of addresses, use the followinng command (and replace the original address file):

    cat <(head -n 1 addresses.csv) <(tail -n +2 addresses.csv | LC_ALL=C sort -u) > addresses_unique.csv


## Entity computation

Bitcoingraph supprts computation of entites as described by [Ron and Shamir](https://eprint.iacr.org/2012/584.pdf). The following command computes entities for a given blockchain data dump:

    bcgraph-compute-entities -i block_1_1000

This creates two additional files:

* entities.csv: list of entity identifiers
* belongs_to_csv: assignment of addresses to entities


## Neo4J graph database setup

Bitcoingraph uses Neo4J as graph database backend. Exported transactions can be imported as follows:


Make sure Neo4J is not running an pre-existing databases are removed:

    ./bin/neo4j stop
    rm -rf data/*


The import the dump using Neo4J's CSV importer tool:

    bin/neo4j-import --into data/graph.db --id-type string --nodes:Transaction dump/transactions.csv --nodes:Address dump/addresses.csv --nodes:Entity dump/entities.csv --relationships:INPUT dump/inputs.csv --relationships:OUTPUT dump/outputs.csv --relationships:BELONGS_TO dump/belongs_to.csv


Then start Neo4J

    ./bin/neo4j start

and create unique indexes with the Cypher commands:

    CREATE CONSTRAINT ON (t:Transaction) ASSERT t.txid IS UNIQUE
    CREATE CONSTRAINT ON (a:Address) ASSERT a.address IS UNIQUE

Cypher commands can be entered either in the Neo4j shell or in the web interface (see http://neo4j.com/docs/stable/tools.html).

# Contributors

* [Bernhard Haslhofer](mailto:bernhard.haslhofer@ait.ac.at)
* [Aljosha Judmaier](mailto:judmayer@xylem-technologies.com)
* [Roman Karl](mailto:roman.karl@ait.ac.at)

# License

This library is release Open Source under the [MIT license](http://opensource.org/licenses/MIT).

[bc_core]: https://github.com/bitcoin/bitcoin "Bitcoin Core"
[bc_conf]: https://en.bitcoin.it/wiki/Running_Bitcoin#Bitcoin.conf_Configuration_File "Bitcoin Core configuration file"

