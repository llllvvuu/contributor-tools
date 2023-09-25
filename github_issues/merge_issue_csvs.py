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
    "csvfiles", metavar="N", type=str, nargs="+", help="CSV files to merge"
)
parser.add_argument("-o", "--output", required=True, help="Output csv file.")
parser.add_argument(
    "--encoding", type=str, default="utf8", help="The encoding of the CSV file"
)

args = parser.parse_args()


def read_csv(filename):
    with open(filename, "r", encoding=args.encoding) as file:
        return [row for row in csv.DictReader(file)]


def write_csv(data, filename):
    if data:
        with open(filename, "w", encoding=args.encoding) as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


# Dictionary to hold data with "Issue URL" as the key and the entire row as the value
data_dict = {}

for filename in args.csvfiles:
    for row in read_csv(filename):
        url = row["Issue URL"]
        # Lexicographic sort works for ISO 8601 dates
        if url not in data_dict or row["Updated At"] > data_dict[url]["Updated At"]:
            data_dict[url] = row

# Convert the dictionary values to a list for writing to the CSV
data_list = list(data_dict.values())

write_csv(data_list, args.output)

print(f"Successfully merged {len(args.csvfiles)} files into {args.output}.")
