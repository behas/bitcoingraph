#!/bin/bash

if [ $# -lt 2 ];
then
    echo "This command takes the file to check as well as the file to check against as arguments"
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
TRIES=20

ERROR=0

for i in $(seq 1 $TRIES);
do 
    RLINE=$(($RANDOM % $(wc -l $REF | cut -d" " -f 1)))
    ADDRS=$(sed -n "$RLINE p" $REF)
    OLINE=0
     
    echo -n "Testing line $RLINE: {" 
    for ADDR in $ADDRS;
    do
        MLINE=$(grep -n $ADDR $TEST| cut -d":" -f 1)
        if [ $? == 0 ] && [ $MLINE == $OLINE -o $(($MLINE - $OLINE)) == $MLINE ];
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

if [ $ERROR == 0 ];
then 
    echo
    echo "OK"
else
    echo
    echo "FAILED"
fi
