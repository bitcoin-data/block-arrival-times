#!/usr/bin/env bash
#
# A script to extract block height and header timestamp for all blocks
# from a Bitcoin Core node via the REST interface.

HOST="http://127.0.0.1:8332"

GENESIS="000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
NEXT_HASH=$GENESIS

while true ; do
  while read height time next;
  do
    echo "$height,$time"
    NEXT_HASH=$next
  done <<<$(curl --silent "$HOST/rest/headers/$NEXT_HASH.json?count=2000" | jq -rc '.[] |  ( (.height | tostring) + " " + (.time | tostring) + " " + .nextblockhash )')
  if [ -z $NEXT_HASH ]; then
	  break;
  fi
done
