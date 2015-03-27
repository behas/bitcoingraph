Bitcoingraph - A Python library for extracting and navigating graph structures from the Bitcoin block chain.

[![Build Status](https://travis-ci.org/behas/bitcoingraph.svg?branch=develop)](https://travis-ci.org/behas/bitcoingraph)

[![Coverage Status](https://coveralls.io/repos/behas/bitcoingraph/badge.svg?branch=develop)](https://coveralls.io/r/behas/bitcoingraph?branch=develop)

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
    python setup.py test
    python setup.py install



# bcgraph-generate usage


## Export blockchain transactions to CSV

The Bitcoin blockchain is a pretty large thing. It is recommended to export blockchain subsets, defined by block height range. The following command exports all transactions contained in block range 1 to 1000.

    bcgraph-generate tx_graph 1 1000 -s localhost:8332 -u your_rpcuser -p your_rpcpass -o tx_graph_1_1000.csv


## Create entity graph from previously exported blockchain transactions

Assuming you previously exported transactions to a file `tx_graph.csv`, then you can generate the entity graph. Associated graph files will be stored in a specific output directory (e.g., `etgraph`).

    bcgraph-generate et_graph -t tx_graph.csv -o etgraph



# bcgraph-analyse usage


This script provides command line procedures for running basic analytics procedures on the extracted transaction and entity graphs.

Here are some usage example for search queries. All examples are performed on the graphs containing infromation form the first 1000 Bitcoin blocks.

The respective graphs can be found in the `./tests/data` directory. It is asumed the the complete path to the test directory is exported as `$PATHTOTESTDATA` for all following examples.

```
export PATHTOTESTDATA="`pwd`/tests/data" #execute form git root dir
export BCGANALYSE="python3.4 `pwd`scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log"
```

The examples use the following randomly chosen bitcoin addresses and entities:
* `12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S` mapped to entity `2` in the first 1000 blocks
* `1ByLSV2gLRcuqUmfdYcpPQH8Npm8cccsFg` mapped to entity `5` in the first 1000 blocks
* `1BBz9Z15YpELQ4QP5sEKb1SwxkcmPb5TMs` mapped to entity `450` in the first 1000 blocks

## Get current entity mappings
To get the current entity mappings a valid entity graph in an apropriatly formated entity graph direcetory is required.
An example entity graph containing data from Bitcoin block 1 to 1000 can be found in `./tests/data/et_graph_1-1000`.
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 --addr2et 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
2
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 --et2addr 2
12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
```

## Find flow/edge by bitcoin address or entity
Both graphs (tranaction and entity) can be searched for entities or bitcoin addresses the same way.
It should be noted, that the order of the results is not necessaryly the same for tranaction graph and entity graph.
Moreover the order can change over time since the entity graph as well as the transaction graph evolve.
So do not except the order to be stable.

The repective results are in *csv* format, where one line represents an edge in the tranaction/entity graph.
In both graphs a line represents a bitcoin flow form source to destination, but the fields
are slightly different depening on the queried graph.

One flow is composed as follows:
* *block_height* The block id of the respective block containing the summarized information of this line.
* *edge* The artifically created edge id of in the tranaction/entity graph.
* *src* In case of an tranaction graph this is the source bitcoin address. In case of an entity graph this is a entity id.
* *tgt* The target/destination bitcoin address or enity id respectively.
* *timestamp* The timestamp of the tranaction in which this flow was included.
* *txid* The transaction id in which this flow was included.
* *value* The value of bitcoins tranfered in this flow.

Simple search for enity/address:
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 -f 2
block_height,edge,src,tgt,timestamp,txid,value
170,82,2,96,1231731025,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,10.0
170,83,2,2,1231731025,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,40.0
...
183,102,2,2,1231742062,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,28.0
248,178,2,2,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,18.0
```
```
$ $BCGANALYSE -t $PATHTOTESTDATA/tx_graph_1-1000.csv -f 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
block_height,edge,src,tgt,timestamp,txid,value
170,171,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3,1231731025,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,10.0
170,172,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,1231731025,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,40.0
...
248,260,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,18.0
9,9,COINBASE,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,1231473279,0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9,50.0
```

When working with an tranaction graph it is importent to know that there is **no** direct mapping from bitcoin address input to bitcoin address output in the Bitcoin protokoll.
Therefore, if a bitcoin address is searched and found in as source addresse, it might be possible that there are also other source addresses within the respective tranaction e.g.:
```
$ $BCGANALYSE -t $PATHTOTESTDATA/tx_graph_1-1000.csv -f 1ELmSkQWnqgbBZNzxAZHts3MEYCngqRBeD
block_height,edge,src,tgt,timestamp,txid,value
586,617,1ELmSkQWnqgbBZNzxAZHts3MEYCngqRBeD,19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6,1232029520,4d6edbeb62735d45ff1565385a8b0045f066055c9425e21540ea7a8060f08bf2,250.0
417,429,COINBASE,1ELmSkQWnqgbBZNzxAZHts3MEYCngqRBeD,1231913658,193b51cd0c5a44bf6593e69fea91e9ddd311f610c5c23187552e3347b275b81b,50.0
```
```
$ $BCGANALYSE -t $PATHTOTESTDATA/tx_graph_1-1000.csv -f 19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6
block_height,edge,src,tgt,timestamp,txid,value
586,620,1LfjLrBDYyPbvGMiD9jURxyAupdYujsBdK,19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6,1232029520,4d6edbeb62735d45ff1565385a8b0045f066055c9425e21540ea7a8060f08bf2,250.0
586,617,1ELmSkQWnqgbBZNzxAZHts3MEYCngqRBeD,19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6,1232029520,4d6edbeb62735d45ff1565385a8b0045f066055c9425e21540ea7a8060f08bf2,250.0
586,618,1ADpf5rHERc2PmVAZZFoH7WbougKvkPDVD,19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6,1232029520,4d6edbeb62735d45ff1565385a8b0045f066055c9425e21540ea7a8060f08bf2,250.0
586,616,1DNdPgBZRWjDj1JbVZQEYMv7jvqJF7R4Py,19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6,1232029520,4d6edbeb62735d45ff1565385a8b0045f066055c9425e21540ea7a8060f08bf2,250.0
586,619,1ACWHyRM8rtbt96KauPJprnF2qDQSdPJ54,19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6,1232029520,4d6edbeb62735d45ff1565385a8b0045f066055c9425e21540ea7a8060f08bf2,250.0
```
The coresponding line in the transaction graph *csv* file looks as follows. Note that *src* contains a list of input addresses and
that there would be a line for every output address if the tranaction would have several outputs.
```
txid;src;tgt;value;timestamp;block_height
4d6edbeb62735d45ff1565385a8b0045f066055c9425e21540ea7a8060f08bf2;1DNdPgBZRWjDj1JbVZQEYMv7jvqJF7R4Py,1ELmSkQWnqgbBZNzxAZHts3MEYCngqRBeD,1ADpf5rHERc2PmVAZZFoH7WbougKvkPDVD,1ACWHyRM8rtbt96KauPJprnF2qDQSdPJ54,1LfjLr
BDYyPbvGMiD9jURxyAupdYujsBdK;19QKDUJtx9n7Vaga6nX1bVHdsnT4Khfyi6;250.0;1232029520;586
```

To only get the first occurence of a Bitcoin entitiy/address:
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 -F 2
block_height,edge,src,tgt,timestamp,txid,value
9,919,1,2,1231473279,0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9,50.0
```
```
$ $BCGANALYSE -t $PATHTOTESTDATA/tx_graph_1-1000.csv -F 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
block_height,edge,src,tgt,timestamp,txid,value
9,9,COINBASE,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,1231473279,0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9,50.0
```

## Find direct flow/edge

Find a direct flow/edge between to bitcoin addresses or entities:
```
$$BCGANALYSE -t $PATHTOTESTDATA/tx_graph_1-1000.csv -x 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S -y 1ByLSV2gLRcuqUmfdYcpPQH8Npm8cccsFg
block_height,edge,src,tgt,timestamp,txid,value
248,259,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,1ByLSV2gLRcuqUmfdYcpPQH8Npm8cccsFg,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,10.0
```
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 5
block_height,edge,src,tgt,timestamp,txid,value
248,177,2,5,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,10.0
```
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 450
No direct edge found
```

Find all `COINBASE` flows from mining to entity:
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 -x 1 -y 9
block_height,edge,src,tgt,timestamp,txid,value
268,201,1,9,1231807132,c3f0bb699bcc8a4e0716de45aef74c40aabeb80f7f00b3bdb45e115ee6f5400f,50.0
417,367,1,9,1231913658,193b51cd0c5a44bf6593e69fea91e9ddd311f610c5c23187552e3347b275b81b,50.0
431,383,1,9,1231923141,b6c967d8f3a3d5fe859a12e9f385531655c2c457326845065fc3942da9e19920,50.0
442,395,1,9,1231930435,a739f9909bdf50466fd746e42394fada8e245f29e6f5747fca0a70dec470b75f,50.0
450,404,1,9,1231936030,d8bb7a39f85135c14c37c8d370c97d642b907a791dd235793061e86e094c8d96,50.0
```

## Find indirect flow/edge

Find one indirect flow/edge between two bitcoin addresses or entities:
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 450 -i 3
hop,block_height,edge,src,tgt,timestamp,txid,value
1,183,101,2,3,1231742062,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,1.0
2,187,107,3,5,1231744600,4385fcf8b14497d0659adccfe06ae7e38e0b5dc95ff8a13d7c62035994a0cd79,1.0
3,496,455,5,450,1231965655,a3b0e9e7cddbbe78270fa4182a7675ff00b92872d8df7d14265a2b1e379a9d33,61.0
```

Find all indirect or direct flows/edges between two bitcoin addresses or entities with depth `d`.
The time complexity of this search is `O(b^d)` where `b` is the branching factor of the graph.

The following search shows two possible paths:
```
$ $BCGANALYSE -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 450 -d 3
hop,block_height,edge,src,tgt,timestamp,txid,value
1,183,101,2,3,1231742062,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,1.0
2,187,107,3,5,1231744600,4385fcf8b14497d0659adccfe06ae7e38e0b5dc95ff8a13d7c62035994a0cd79,1.0
3,496,455,5,450,1231965655,a3b0e9e7cddbbe78270fa4182a7675ff00b92872d8df7d14265a2b1e379a9d33,61.0
hop,block_height,edge,src,tgt,timestamp,txid,value
1,248,177,2,5,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,10.0
2,496,455,5,450,1231965655,a3b0e9e7cddbbe78270fa4182a7675ff00b92872d8df7d14265a2b1e379a9d33,61.0
```



# Contributors

* [Bernhard Haslhofer](mailto:bernhard.haslhofer@ait.ac.at)

# License

This library is release Open Source under the [MIT license](http://opensource.org/licenses/MIT).

[bc_core]: https://github.com/bitcoin/bitcoin "Bitcoin Core"
[bc_conf]: https://en.bitcoin.it/wiki/Running_Bitcoin#Bitcoin.conf_Configuration_File "Bitcoin Core configuration file"

