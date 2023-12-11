# she bang

import csv
import glob

rows = list()

for file in glob.glob('data/*.csv'):
    print(f"reading CSV file {file}")
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            height = row[0]
            bhash = row[1]
            timestamp = row[2]
            source = file.split("/")[-1].replace(".csv", "")
            rows.append([height, bhash, timestamp, source])


with open('timestamps.csv', 'w') as csvfile:
    print(f"writing combined CSV file timestamps.csv")
    writer = csv.writer(csvfile)
    for row in sorted(rows, reverse=True):
        writer.writerow(row)

