#!/usr/bin/env bash
#
# Basic sanity checks for $FILE

FILE="timestamps.csv"

echo "Checking if $FILE is sorted (ascending) and only contains unique entries.."
echo "Using LC_ALL=C for determinitic sorting"
LC_ALL=C sort --reverse --check --unique $FILE
