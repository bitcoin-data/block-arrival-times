#!/usr/bin/env python3

import csv

ARRIVAL_TIMESTAMP_FILE = "timestamps.csv"

min_max_time_per_source = dict()

with open(ARRIVAL_TIMESTAMP_FILE, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        _, __, timestamp, source = row
        if source not in min_max_time_per_source:
            min_max_time_per_source[source] = {
                "min": timestamp, "max": timestamp}
        if timestamp < min_max_time_per_source[source]["min"]:
            min_max_time_per_source[source]["min"] = timestamp
        if timestamp > min_max_time_per_source[source]["max"]:
            min_max_time_per_source[source]["max"] = timestamp

    mermaid_rows = ""
    for source in min_max_time_per_source:
        mermaid_rows += f"{source}: {min_max_time_per_source[source]['min']}, {min_max_time_per_source[source]['max']}" + "\n"

    mermaid = f"""
```mermaid
gantt
dateFormat x
title data availability (not showing potential per-source holes)
todayMarker off

{mermaid_rows}
```"""
    print(mermaid)
