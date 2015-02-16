#!/bin/bash
# This scripts verifies the entity graph mapping by using 
# data from previous research for example by Harrigan et al. 
# http://arxiv.org/pdf/1107.4524v2.pdf
# The according data can be optained from here:
# http://anonymity-in-bitcoin.blogspot.co.at/2011/09/code-datasets-and-spsn11.html

if [ $# -lt 2 ];
then
    echo "This command takes three arguments"
    echo "  \$1  File to check"
    echo "  \$2  File to check against i.e. reference"
    echo "  \$3  Size of sample set to verify, 0 for all"
    exit
fi 
# The file to test in the format:
#<entity>,<btcaddrs> <btcaddr> ...
#123,asdf qwer ...
TEST=$1
# This is the reference file in the format:
#<btcaddr> <btcaddr> ...
#asdf qwer ...
REF=$2

# The number of lines which should be compared 
# Set to 0 for comparing all
TRIES=$3

RLINES=$(wc -l $REF | cut -d" " -f 1)
# Error flag
ERROR=0


echo "Test file     : $TEST"
echo "Reference file: $REF"
echo "Testing ..."

function testsampleset {
    for i in $(seq 1 $TRIES);
    do 
        RLINE=$(($RANDOM % $RLINES))
        ADDRS=$(sed -n "$RLINE p" $REF)
        OLINE=0
         
        echo -n "Testing line $RLINE: {" 
        for ADDR in $ADDRS;
        do
            MLINE=$(grep -n $ADDR $TEST| cut -d":" -f 1)
            if [[ $? == 0 && ( $MLINE == $OLINE || $(($MLINE - $OLINE)) == $MLINE ) ]];
            then
                echo -n "'$ADDR': $MLINE, "
            else
                echo -n "'$ADDR': None,"
                ERROR=1 
            fi
            OLINE=$MLINE
        done
        echo "}"
    done
}

function testall {
    for RLINE in $(seq 1 $RLINES);
    do 
        ADDRS=$(sed -n "$RLINE p" $REF)
        OLINE=0
         
        echo -n "Testing line $RLINE: {" 
        for ADDR in $ADDRS;
        do
            MLINE=$(grep -n $ADDR $TEST| cut -d":" -f 1)
            if [[ $? == 0 && ( $MLINE == $OLINE || $(($MLINE - $OLINE)) == $MLINE ) ]];
            then
                echo -n "'$ADDR': $MLINE, "
            else
                echo -n "'$ADDR': None,"
                ERROR=1 
            fi
            OLINE=$MLINE
        done
        echo "}"
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
