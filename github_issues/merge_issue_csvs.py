__author__ = "GPT-4"

import argparse
import csv
import sys

# Increase max CSV field size
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

parser = argparse.ArgumentParser(description="Merge and deduplicate csv files.")
parser.add_argument(
    "csvfiles", metavar="N", type=str, nargs="+", help="an integer for the accumulator"
)
parser.add_argument("-o", "--output", required=True, help="Output csv file.")

args = parser.parse_args()


def read_csv(filename):
    with open(filename, "r") as file:
        return [row for row in csv.DictReader(file)]


def write_csv(data, filename):
    if data:
        with open(filename, "w") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


data = []
urls = set()

for filename in args.csvfiles:
    for row in read_csv(filename):
        if row["Issue URL"] not in urls:
            data.append(row)
            urls.add(row["Issue URL"])

write_csv(data, args.output)

print(f"Successfully merged {len(args.csvfiles)} files into {args.output}.")
