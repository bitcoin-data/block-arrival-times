#!/usr/bin/env python3

import csv
import statistics


BLOCK_TIMESTAMP_FILE = "qa/block-timestamps/block-timestamps.csv"
ARRIVAL_TIMESTAMP_FILE = "timestamps.csv"
MAX_DEVIATION_MS = 1000 * 60 * 60 * 2  # 2h

print("Checking that timestamps don't deviate too much from block header timestamps")

height_to_timestamp = dict()

has_error = False

with open(BLOCK_TIMESTAMP_FILE) as f:
    reader = csv.reader(f)
    for row in reader:
        height_str, timestamp_str = row
        height = int(height_str)
        timestamp = int(timestamp_str)
        height_to_timestamp[height] = timestamp
    print(
        f"Imported {len(height_to_timestamp)} timestamps from {BLOCK_TIMESTAMP_FILE}")

per_source_offset = dict()

print(f"Checking {ARRIVAL_TIMESTAMP_FILE}...")
with open(ARRIVAL_TIMESTAMP_FILE) as f:
    reader = csv.reader(f)
    for row in reader:
        height_str, header, timestamp_str, source = row
        height = int(height_str)
        timestamp = int(timestamp_str)
        if height not in height_to_timestamp:
            print(
                f"ERROR: Could not lookup height {height}. Please update {BLOCK_TIMESTAMP_FILE}.")
            exit(1)
        else:
            block_timestamp = height_to_timestamp[height]
            block_timestamp_ms = block_timestamp * 1000
            timestamp_offset_ms = timestamp - block_timestamp_ms
            if source not in per_source_offset:
                per_source_offset[source] = list()
            per_source_offset[source].append(timestamp_offset_ms / 1000)

            if timestamp > block_timestamp_ms + MAX_DEVIATION_MS:
                print(
                    f"ERROR: Timestamp for block {height} ({header}) from source {source} deviates more that {MAX_DEVIATION_MS / 1000}s into the future: {timestamp_offset_ms / 1000}s")
                has_error = True

            if timestamp < block_timestamp_ms - MAX_DEVIATION_MS:
                print(
                    f"ERROR: Timestamp for block {height} ({header}) from source {source} deviates more that {MAX_DEVIATION_MS / 1000}s into the past: {timestamp_offset_ms / 1000}s")
                has_error = True

if not has_error:
    print("No offset problems found.")

print("\nStatistics about offsets from block timestamps:")

template = "{:<25} {:<10} {:<10} {:<12} {:<12} {:<12} {}"
print(template.format("source", "count", "min",
      "max", "mean", "stdev", "quantiles[s]"))
for source in per_source_offset:
    offsets = per_source_offset[source]
    print(template.format(
        source,
        "{}".format(len(offsets)),
        "{:.0f}s".format(min(offsets)),
        "{:.0f}s".format(max(offsets)),
        "{:.2f}s".format(statistics.mean(offsets)),
        "{:.2f}s".format(statistics.stdev(offsets)),
        "{}".format(statistics.quantiles(offsets))))

if has_error:
    print("\nCheck not successful.")
    print("The listed timestamps might have been recorded during IBD or the system clock was wrong?")
    exit(1)
else:
    print("\nCheck successful.")
