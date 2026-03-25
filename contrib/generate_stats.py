#!/usr/bin/env python3
"""Generate pre-computed statistics for the block-arrival-times website.

Run from the repo root:
    python3 contrib/generate_stats.py

Outputs: docs/stats.json
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
BLOCK_TIMESTAMPS_FILE = Path("qa/block-timestamps/block-timestamps.csv")
OUTPUT_DIR = Path("docs")
OUTPUT_FILE = OUTPUT_DIR / "stats.json"

BUCKET_SIZE = 1008 # one week


def percentile(sorted_data, p):
    if not sorted_data:
        return None
    idx = max(0, min(int(len(sorted_data) * p / 100), len(sorted_data) - 1))
    return sorted_data[idx]


print("Loading reference block timestamps...")
block_timestamps = {}  # height -> unix timestamp (seconds)
with open(BLOCK_TIMESTAMPS_FILE) as f:
    for row in csv.reader(f):
        block_timestamps[int(row[0])] = int(row[1])

global_max_height = max(block_timestamps)

# Pre-compute how many reference blocks fall in each bucket
bucket_ref_count = {}
for h in block_timestamps:
    b = h // BUCKET_SIZE
    bucket_ref_count[b] = bucket_ref_count.get(b, 0) + 1

sources_data = []

for csv_file in sorted(DATA_DIR.glob("*.csv")):
    name = csv_file.stem
    print(f"  {name} ...", flush=True)

    # Keep the earliest arrival timestamp per block height
    blocks = {}  # height -> timestamp_ms
    with open(csv_file) as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            h, ts_ms = int(row[0]), int(row[2])
            if h not in blocks or ts_ms < blocks[h]:
                blocks[h] = ts_ms

    if not blocks:
        continue

    height_min = min(blocks)
    height_max = max(blocks)

    # Delta: arrival_ms - header_timestamp_sec * 1000
    deltas_ms = sorted(
        blocks[h] - block_timestamps[h] * 1000
        for h in blocks
        if h in block_timestamps
    )

    delta_stats = {
        "p25":   percentile(deltas_ms, 25),
        "p50":   percentile(deltas_ms, 50),
        "p75":   percentile(deltas_ms, 75),
        "count": len(deltas_ms),
    }

    # Coverage: fraction of reference blocks present in each 1008-block bucket
    bucket_present = {}
    for h in blocks:
        b = h // BUCKET_SIZE
        bucket_present[b] = bucket_present.get(b, 0) + 1

    b_min = height_min // BUCKET_SIZE
    b_max = height_max // BUCKET_SIZE
    coverage = [
        [b, round(bucket_present.get(b, 0) / bucket_ref_count[b], 3)]
        for b in range(b_min, b_max + 1)
        if b in bucket_ref_count
    ]

    sources_data.append({
        "name":             name,
        "block_count":      len(blocks),
        "height_min":       height_min,
        "height_max":       height_max,
        "timestamp_min_ms": min(blocks.values()),
        "timestamp_max_ms": max(blocks.values()),
        "delta_stats_ms":   delta_stats,
        "coverage":         coverage,  # [[bucket_idx, fraction], ...]
    })

# Newest sources first
sources_data.sort(key=lambda s: s["timestamp_min_ms"], reverse=True)

# Trim the visible range to where data actually starts
data_height_min = min(s["height_min"] for s in sources_data)
data_height_max = max(s["height_max"] for s in sources_data)
bucket_min = data_height_min // BUCKET_SIZE
bucket_max = data_height_max // BUCKET_SIZE

OUTPUT_DIR.mkdir(exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    json.dump({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bucket_size":  BUCKET_SIZE,
        "height_min":   data_height_min,
        "height_max":   data_height_max,
        "bucket_min":   bucket_min,
        "bucket_max":   bucket_max,
        "sources":      sources_data,
    }, f, separators=(",", ":"))

size_kb = OUTPUT_FILE.stat().st_size // 1024
print(f"\nWrote {OUTPUT_FILE} ({size_kb} KB), {len(sources_data)} sources")
