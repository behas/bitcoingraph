#!/bin/bash

if [ $# -lt 1 ];
then
    echo "This command takes one arguments"
    echo "  \$1  the transaction dump directory"
    exit
fi 

DUMPDIR="$1"

ADDR_FILE="${DUMPDIR}/addresses.csv"

TEMP_FILE="${DUMPDIR}/temp.csv"

TEMP_FILE_SORTED="${DUMPDIR}/temp_sorted.csv"

RESULT="${DUMPDIR}/addresses_unique.csv"


echo "Copy addresses from ${ADDR_FILE} to ${TEMP_FILE} (with removed CSV header)"
tail -n +2 "${ADDR_FILE}" > "${TEMP_FILE}"

echo "Sorting and deduplicating ${TEMP_FILE}"
sort "${TEMP_FILE}" | uniq > "${TEMP_FILE_SORTED}"

echo "Adding removed CSV header and deduplicated data to ${RESULT}"
CSV_HEADER=$(head -n 1 ${ADDR_FILE})
echo $CSV_HEADER
echo "${CSV_HEADER}" > "${RESULT}"
cat "${TEMP_FILE_SORTED}" >> "${RESULT}"

echo "Cleaning up..."
rm "${TEMP_FILE}"
rm "${TEMP_FILE_SORTED}"

echo "Finished deduplication process."
