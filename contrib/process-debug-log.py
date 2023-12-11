#!/usr/bin/env python3

import argparse
import csv
import datetime
import re

UPDATE_TIP = "UpdateTip: new best="
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"  # ISO 8601
MIN_PROGRESS = float(0.99999)
MAX_TIME_DELTA = datetime.timedelta(hours=1)
DESCRIPTION = "Parses a Bitcoin Core debug.log file and prints the block arrival times in CSV format."


PATTERN_FLOAT = r"\d*\.\d+"
PATTERN_HASH = r"[a-f0-9]+"
PATTERN_HEX = r"0x[a-f0-9]+"
PATTERN_NOT_QUOTE = "[^'\"]+"
PATTERN_UPDATE_TIP_START = "UpdateTip: "

# 'UpdateTip: ...' subpatterns. Grab whatever of this we can - lot of
# variation between Bitcoin Core versions.
PATTERN_UPDATE_TIP_SUB = {
    re.compile(rf"new\s+best=(?P<blockhash>{PATTERN_HASH})\s+"),
    re.compile(r"\s+height=(?P<height>\d+)\s+"),
    # Early date format
    re.compile(r"\s+date='?(?P<date>[0-9-]+ [0-9:]+)'?\s+"),
    # Later date format
    re.compile(rf"\s+date='(?P<date>{PATTERN_NOT_QUOTE})'\s+"),
    # Sync progress
    re.compile(rf"\s+progress=(?P<progress>{PATTERN_FLOAT}) "),
}

def get_time(line: str = "", timestr: str = "") -> datetime.datetime:
    """
    Return the time a log message was emitted in UTC.
    """
    if not (line or timestr):
        raise ValueError("arg required")
    if not timestr:
        timestr = line.split()[0]

    # fromisofromat() does not handle the Z postfix
    timestr = timestr.replace("Z", "+00:00")

    d = datetime.datetime.fromisoformat(timestr.strip())

    # Ensure any date we parse is tz-aware.
    assert (offset := d.utcoffset()) is not None

    return d + offset


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "input", help="Debug log file used as input.", type=argparse.FileType('r'))
    parser.add_argument("output", help="CSV output file.",
                        type=argparse.FileType('w'))
    args = parser.parse_args()

    print(f"Reading from {args.input.name} and writing to {args.output.name}:")

    writer = csv.writer(args.output, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    process(args.input, writer)


def process(inputf, writer):
    skipped = 0
    written = 0

    for line in inputf.readlines():
        matchgroups = {}
        if line.find(PATTERN_UPDATE_TIP_START) != -1:
            for patt in PATTERN_UPDATE_TIP_SUB:
                if match := patt.search(line):
                    matchgroups.update(match.groupdict())

            timestamp = get_time(line)

            # Bitcoin Core 0.12 has UpdateTip: lines that just display the warning, so skip those.
            if "height" not in matchgroups or "blockhash" not in matchgroups:
                print(f"Skipping line: {line}")
                skipped += 1
                continue

            height = int(matchgroups["height"])
            blockhash = matchgroups["blockhash"]

            if "progress" not in matchgroups and "date" not in matchgroups:
                print("Neither 'progress' nor 'date' in line. Skipping: {line}")
                skipped += 1
                continue

            progress = float(matchgroups["progress"])
            date = get_time(matchgroups["date"])
            timedelta = timestamp - date

            timestamp_ms = int(datetime.datetime.timestamp(timestamp)*1000)

            if check(blockhash, timedelta, progress):
                output(writer, timestamp_ms, blockhash, height)
                written += 1
            else:
                print(f"Skipping block height={height} hash={blockhash} with timedelta={timedelta} and progress={progress}")
                skipped += 1

    print(f"Written {written} blocks and skipped {skipped} blocks.")


def check(bhash, timedelta, progress) -> bool:
    assert(progress > 0)
    assert(progress <= 1)
    assert(len(bhash) == 64)

    if timedelta > MAX_TIME_DELTA or timedelta < - MAX_TIME_DELTA:
        return False

    if progress < MIN_PROGRESS:
        return False

    return True


def output(writer, time, bhash, height):
    writer.writerow([height, bhash, time])


if __name__ == '__main__':
    main()
