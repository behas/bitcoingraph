#!/bin/bash

if [ $# -lt 2 ];
then
    echo "This command takes three arguments"
    echo "  \$1  et_graph directory"
    echo "  \$2  depth to search"
    echo "  \$3  0 for random, n for source"
    echo "  \$4  destination start value"
    exit
fi 

ETDIR="$1"
ETMAP="$ETDIR/etmap.csv"
ETG="$ETDIR/etg.csv"

DEPTH="$2"
SRC="$3"
DST="$4"

PYTHON="/usr/bin/python3.4"
SCRIPT="$PYTHON ./scripts/bcgraph-analyse"

FOUND=0
RESULT=""
MAXET=$(wc -l "$ETMAP" | cut -d" " -f 1)

echo "Search et_graph dir: $ETDIR"
echo "              etmap: $ETMAP"
echo " number of entities: $MAXET"
echo "                etg: $ETG"
echo "              depth: $DEPTH"
echo "             source: $SRC"

function findany {
    for i in $(seq 1 $MAXET);
    do 
        SRC=$(($RANDOM % $MAXET))
        DST=$(($RANDOM % $MAXET))
        CMD="$SCRIPT -l DEBUG --logfile /tmp/analyse.log -e $ETDIR -x $SRC -y $DST -i $DEPTH"
        echo $CMD
        RESULT=$($CMD)
        if [ $? == 0 ] 
        then
            FOUND=1
            echo 
            echo "FOUND:"
            echo  
            echo "$RESULT"
            break
        fi
        #echo $RESULT

    done   
} 
function finddst { 
    for i in $(seq 1 $MAXET);
    do 
        DST=$(($DST + 1))
        CMD="$SCRIPT -l DEBUG --logfile /tmp/analyse.log -e $ETDIR -x $SRC -y $DST -i $DEPTH"
        echo $CMD
        RESULT=$($CMD)
        if [ $? == 0 ] 
        then
            FOUND=1
            echo 
            echo "FOUND:"
            echo  
            echo "$RESULT"
            break
        fi
        #echo $RESULT

    done   
}


if [ $SRC == 0 ];
then
    echo "Searching for any indirect flow randomly ..."
    findany
else
    echo "Searching all indirect flows form src to any dst ..."
    finddst
fi


if [ $FOUND == 1 ];
then 
    echo
    echo "OK"
else
    echo
    echo "FAILED"
fi
