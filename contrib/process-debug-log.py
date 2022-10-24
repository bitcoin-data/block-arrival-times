#!/usr/bin/env python3

import argparse
import csv
import datetime

UPDATE_TIP = "UpdateTip: new best="
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"  # ISO 8601
MIN_PROGRESS = float(0.99999)
MAX_TIME_DELTA = datetime.timedelta(hours=1)
DESCRIPTION = "Parses a Bitcoin Core debug.log file and prints the block arrival times in CSV format."


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "input", help="Debug log file used as input.", type=argparse.FileType('r'))
    parser.add_argument("output", help="CSV output file.",
                        type=argparse.FileType('w'))
    parser.add_argument(
        "source", help="Debug log file source (e.g. the person that provided it).")
    args = parser.parse_args()

    print(
        f"Reading from {args.input.name} and writing to {args.output.name} with the source name: '{args.source}'")

    writer = csv.writer(args.output, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    process(args.input, writer, args.source)


def process(inputf, writer, source):
    skipped = 0
    written = 0

    for line in inputf.readlines():
        split_line = line.split(" ", 1)
        if len(split_line) == 2:
            time, msg = split_line
            if msg.startswith(UPDATE_TIP):
                arrival_time = datetime.datetime.strptime(
                    time, TIMESTAMP_FORMAT)
                arrival_timestamp = int(
                    datetime.datetime.timestamp(arrival_time)*1000)

                # UpdateTip: new best=0000000000000000000483a9db499b02afa028f963c2ac991c4beec8827b8e9b height=726259 version=0x2051c004 log2_work=93.387104 tx=715739617 date='2022-03-07T11:36:50Z' progress=0.947769 cache=14.4MiB(105915txo)
                msg_parts = msg.split(" ")
                # part 2: "best=<hash>"
                part2 = msg_parts[2]
                # part 3: "height=<height>"
                part3 = msg_parts[3]
                # part 7: "date=<header_date>"
                part7 = msg_parts[7]
                # part 8: "progress=<progress>"
                part8 = msg_parts[8]

                bhash = part2.replace("best=", "")
                height = int(part3.replace("height=", ""))
                date_str = part7.replace("date=", "").replace("'", "")
                date = datetime.datetime.strptime(date_str, TIMESTAMP_FORMAT)
                timedelta = arrival_time - date
                progress = float(part8.replace("progress=", ""))

                if check(bhash, timedelta, progress):
                    output(writer, arrival_timestamp, bhash, height, source)
                    written += 1
                else:
                    print(
                        f"Skipping block height={height} hash={bhash} with timedelta={timedelta} and progress={progress}")
                    skipped += 1
    print(f"Written {written} blocks and skipped {skipped} blocks.")


def check(bhash, timedelta, progress):
    assert(progress > 0)
    assert(progress <= 1)
    assert(len(bhash) == 64)

    if timedelta > MAX_TIME_DELTA or timedelta < - MAX_TIME_DELTA:
        return False

    if progress < MIN_PROGRESS:
        return False

    return True


def output(writer, time, bhash, height, source):
    writer.writerow([height, bhash, time, source])


if __name__ == '__main__':
    main()
