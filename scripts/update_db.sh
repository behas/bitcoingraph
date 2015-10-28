#!/bin/bash

number_of_blocks=$1
start_block_hash=$2
path=$3

../utils/export_test.py $number_of_blocks -b $start_block_hash -o $path --plain-header --no-separate-header

python update_db.py $path