Bitcoingraph - A Python Bitcoin library supporting
* navigation along Bitcoin blocks and transactions
* generation of various type of data graphs from the Bitcoin blockchain

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

    git clone git@bitbucket.org:bhaslhofer/bitcoingraph.git


...test and install the Bitcoingraph library:

    cd bitcoingraph
    python setup.py test
    python setup.py install


# CLI Usage


## Export transaction graph CSV from blockchain

The Bitcoin blockchain is a pretty large thing. It is recommended to export blockchain subsets, defined by block height range. The following command exports all transactions contained in block range 1 to 1000.

    bcgraph-generate tx_graph 1 1000 -s localhost:8332 -u your_rpcuser -p your_rpcpass -o tx_graph_1_1000.csv



# Contributors

* [Bernhard Haslhofer](mailto:bernhard.haslhofer@ait.ac.at)

# License

This library is release Open Source under the [MIT license](http://opensource.org/licenses/MIT).



[bc_core]: https://github.com/bitcoin/bitcoin "Bitcoin Core"
[bc_conf]: https://en.bitcoin.it/wiki/Running_Bitcoin#Bitcoin.conf_Configuration_File "Bitcoin Core configuration file"
