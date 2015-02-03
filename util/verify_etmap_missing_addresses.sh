#!/bin/bash

if [ $# -lt 2 ];
then
    echo "This command takes two arguments"
    echo "  \$1  File of missing bitcoin addresses"
    echo "  \$2  File of tx_graph input addresses"
    exit
fi 
# The Missing bitcoin addresses from the test_etmap_csv.sh
# in the format:
#<btcaddrs> 
# This can be generated as follows:
#
MBTC=$1
# The Input addresses of the tx_graph in the format:
#<btcaddr> 
# This can be generated as follows
IBTC=$2

# The number of lines which should be compared 
# Set to 0 for comparing all
TRIES=0

MLINES=$(wc -l $MBTC | cut -d" " -f 1)
# Error flag
ERROR=0

echo "Missing btc addr. file : $TEST"
echo "Input  btc addr. file  : $REF"
echo "Testing ..."

function testsampleset {
    for i in $(seq 1 $TRIES);
    do 
        MLINE=$(($RANDOM % $MLINES))
        ADDR=$(sed -n "$MLINE p" $MBTC)
        OLINE=0
         
        echo -n "'$ADDR':$MBTC:$MLINE:$IBTC:"
        grep $ADDR $IBTC
        if [[ $? != 0 ]];
        then
            echo "NOT_FOUND"
        else
            echo "FOUND"
            ERROR=1 
        fi
    done
}

function testall {
    for i in $(seq 1 $MLINES);
    do 
        MLINE=$i
        ADDR=$(sed -n "$MLINE p" $MBTC)
        OLINE=0
         
        echo -n "'$ADDR':$MBTC:$MLINE:$IBTC:"
        grep $ADDR $IBTC
        if [[ $? != 0 ]];
        then
            echo "NOT_FOUND"
        else
            echo "FOUND"
            ERROR=1 
        fi

    done   
} 

if [ $TRIES == 0 ];
then
    testall
else
    testsampleset
fi


if [ $ERROR == 0 ];
then 
    echo
    echo "OK"
else
    echo
    echo "FAILED"
fi
