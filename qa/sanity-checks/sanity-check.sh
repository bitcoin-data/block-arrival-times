#!/usr/bin/env bash
#
# Basic sanity checks for $FILE

FILE="../../timestamps.csv"

echo "Checking if $FILE is sorted (ascending) and only contains unique entries..."
sort --reverse --check --unique timestamps.csv
