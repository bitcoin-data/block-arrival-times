#!/usr/bin/env bash
#
# Checks if the mermaid gantt graph in the README is up-to-date.

tmp_README=$(mktemp)
tmp_GENERATED=$(mktemp)

sed -n '/```mermaid/,/```/p' README.md > $tmp_README
python3 qa/data-availability/gen-mermaid.py | sed -n '/```mermaid/,/```/p' > $tmp_GENERATED

diff_output=$(diff $tmp_README $tmp_GENERATED --color=always --minimal)

rm $tmp_README
rm $tmp_GENERATED

if [[ -z $diff_output ]]; then
    echo "The gantt chart in the README.md is up-to-date."
else
    echo "The gantt chart in the README.md is NOT up-to-date. Diff does not match:"
    echo $diff_output
    exit 1
fi
