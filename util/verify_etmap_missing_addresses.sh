#!/bin/bash
# This script should check missing addresses that
# have been found in the reference dataset but not in the
# actual enity mapping. 
# A possible cause for that is that the reference dataset includes 

if [ $# -lt 2 ];
then
    echo "This command takes two arguments"
    echo "  \$1  File of missing bitcoin addresses"
    echo "  \$2  File of tx_graph input addresses"
    exit
fi 
# The Missing bitcoin addresses from the verify_etmap_csv.sh
# in the format:
#<btcaddrs> 
# This can be generated as follows:
# $ grep -En '\{.[0-9a-zA-Z]{20,35}.\:\s*None\,\}' verify_etmap_csv.log | cut -d"'" -f 2 > verify_negative.log
# To be sure that there are only missing entitys that consist 
# of single bitcoin addresses quickly check if the following
# files have the same length
# $ grep -En '\:\s*None' verify_etmap_csv.log > verify_negative_all.log
# $ grep -En '\{.[0-9a-zA-Z]{20,35}.\:\s*None\,\}' verify_etmap_csv.log > verify_negative_single.log
# $ wc -l verify_negative*
MBTC=$1

# The Input addresses of the tx_graph in the format:
#<btcaddr> 
# This can be generated as follows:
# $ cut -d";" -f 2 tx_graph_1-136165_2015-01-26.csv > tx_graph_1-136165_2015-01-26.csv_f2 
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
