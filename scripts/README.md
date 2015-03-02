# bcgraph-analyse examples (block 1-1000)
Some example use-cases for search queries

## Find flow/edge by ...
Search for the following Bitcoin addresses and Entities:
* `12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S` Entity = `2`
* `1ByLSV2gLRcuqUmfdYcpPQH8Npm8cccsFg` Entity = `5`
* `1BBz9Z15YpELQ4QP5sEKb1SwxkcmPb5TMs` Entity = `450`

On the command line the same can be accieved by the following commands. 
To get entity mappings the entity graph is required:
```
$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 --addr2et 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
2
$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 --et2addr 2
12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
```

Both graphs can be searches for entities or bitcoin addresses:
```
$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 -f 2
src,txid,block_height,timestamp,tgt,value,edge
2,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,170,1231731025,96,10.0,82
2,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,170,1231731025,2,40.0,83
2,a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be,181,1231740133,109,10.0,96
2,a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be,181,1231740133,2,30.0,97
2,591e91f809d716912ca1d4a9295e70c3e78bab077683f79350f101da64588073,182,1231740736,4,1.0,99
2,591e91f809d716912ca1d4a9295e70c3e78bab077683f79350f101da64588073,182,1231740736,2,29.0,100
2,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,183,1231742062,3,1.0,101
2,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,183,1231742062,2,28.0,102
2,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,248,1231790660,5,10.0,177
2,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,248,1231790660,2,18.0,178
1,0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9,9,1231473279,2,50.0,919
2,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,170,1231731025,2,40.0,83
2,a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be,181,1231740133,2,30.0,97
2,591e91f809d716912ca1d4a9295e70c3e78bab077683f79350f101da64588073,182,1231740736,2,29.0,100
2,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,183,1231742062,2,28.0,102
2,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,248,1231790660,2,18.0,178

$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -t $PATHTOTESTDATA/tx_graph_1-1000.csv -f 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
value,edge,tgt,txid,timestamp,block_height,src
10.0,171,1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,1231731025,170,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
40.0,172,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,1231731025,170,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
10.0,184,1DUDsfc23Dv9sPMEk5RsrtfzCw5ofi5sVW,a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be,1231740133,181,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
30.0,185,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be,1231740133,181,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
1.0,187,1LzBzVqEeuQyjD2mRWHes3dgWrT9titxvq,591e91f809d716912ca1d4a9295e70c3e78bab077683f79350f101da64588073,1231740736,182,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
29.0,188,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,591e91f809d716912ca1d4a9295e70c3e78bab077683f79350f101da64588073,1231740736,182,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
1.0,190,13HtsYzne8xVPdGDnmJX8gHgBZerAfJGEf,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,1231742062,183,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
28.0,191,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,1231742062,183,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
10.0,259,1ByLSV2gLRcuqUmfdYcpPQH8Npm8cccsFg,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,1231790660,248,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
18.0,260,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,1231790660,248,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
50.0,9,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9,1231473279,9,COINBASE
40.0,172,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,1231731025,170,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
30.0,185,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be,1231740133,181,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
29.0,188,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,591e91f809d716912ca1d4a9295e70c3e78bab077683f79350f101da64588073,1231740736,182,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
28.0,191,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,1231742062,183,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
18.0,260,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,1231790660,248,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S
```

To only get the first occurence of Bitcoin address/Enitiy:
```
$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 -F 2
timestamp,edge,value,txid,block_height,src,tgt
1231473279,919,50.0,0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9,9,1,2
```

## Find direct flow/edge

Find a direct edge/flow between to bitcoin addresses or entities:
```
$python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -t $PATHTOTESTDATA/tx_graph_1-1000.csv -x 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S -y 1ByLSV2gLRcuqUmfdYcpPQH8Npm8cccsFg
block_height,edge,src,tgt,timestamp,txid,value
248,259,12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S,1ByLSV2gLRcuqUmfdYcpPQH8Npm8cccsFg,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,10.0

$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 5
block_height,edge,src,tgt,timestamp,txid,value
248,177,2,5,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,10.0

$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 450
No direct edge found
```

Find all `COINBASE` flows from mining to entity:
```
$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 -x 1 -y 9
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
$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 450 -i 3
hop,block_height,edge,src,tgt,timestamp,txid,value
1,183,101,2,3,1231742062,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,1.0
2,187,107,3,5,1231744600,4385fcf8b14497d0659adccfe06ae7e38e0b5dc95ff8a13d7c62035994a0cd79,1.0
3,496,455,5,450,1231965655,a3b0e9e7cddbbe78270fa4182a7675ff00b92872d8df7d14265a2b1e379a9d33,61.0
```

Find all indirect or direct flows/edges between two bitcoin addresses or entities with depth `d`:
```
$ python3.4 scripts/bcgraph-analyse -l DEBUG --logfile /tmp/analyse.log -e $PATHTOTESTDATA/et_graph_1-1000 -x 2 -y 450 -d 3
hop,block_height,edge,src,tgt,timestamp,txid,value
1,183,101,2,3,1231742062,12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba,1.0
2,187,107,3,5,1231744600,4385fcf8b14497d0659adccfe06ae7e38e0b5dc95ff8a13d7c62035994a0cd79,1.0
3,496,455,5,450,1231965655,a3b0e9e7cddbbe78270fa4182a7675ff00b92872d8df7d14265a2b1e379a9d33,61.0
hop,block_height,edge,src,tgt,timestamp,txid,value
1,248,177,2,5,1231790660,828ef3b079f9c23829c56fe86e85b4a69d9e06e5b54ea597eef5fb3ffef509fe,10.0
2,496,455,5,450,1231965655,a3b0e9e7cddbbe78270fa4182a7675ff00b92872d8df7d14265a2b1e379a9d33,61.0
```
