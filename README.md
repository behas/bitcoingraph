Bitcoingraph - A Python Bitcoin library supporting
* navigation along Bitcoin blocks and transactions
* generation of various type of data graphs from the Bitcoin blockchain

# Prerequesites

## Bitcoin Core setup and configuration

Install the current version of Bitcoin Core, either from [source](https://github.com/bitcoin/bitcoin) or from a [pre-compiled executable](https://bitcoin.org/en/download).

Once installed, you'll have access to three programs: `bitcoind` (= full peer), `bitcoin-qt` (= )


bitcoingraph accesses blockchain data via the Bitcoin client's JSON-RPC
API. So first, make sure that the [Bitcoin Core client][bc_client] is running on your machine. Try

    bitcoind -printoconsole

Second, make sure that your bitcoin client accepts JSON-RPC connections.


## Other requirements

Make sure Python 3.4 is installed on your machine

    bitcoin-graph git:(master) ✗ python --version
    Python 3.4.0

# Bitcoin setup


# Howto...


## ...generate the transaction graph from the blockchain


## ...generate the entity graph from the transaction graoh


## ...generate the identiy graph from the entity graph


# Contributors

* Bernhard Haslhofer

# License

tbd (Apache, etc)


[bc_core]: https://github.com/bitcoin/bitcoin "Bitcoin Core"
