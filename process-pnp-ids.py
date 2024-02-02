#!/usr/bin/env python3

import argparse
import csv
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process UEFI CSV output.")
    parser.add_argument(
        "csv_file", metavar="INPUT", type=argparse.FileType("r"), help="input CSV file"
    )
    parser.add_argument(
        "output_file", metavar="OUTPUT", type=argparse.FileType("w"), help="output file"
    )

    args = parser.parse_args()
    output_lines = []

    reader = csv.DictReader(args.csv_file)
    for row in reader:
        if len(row) != 3:
            print(f"Invalid line: {row}", file=sys.stderr)
            continue
        pnp_id = row["PNP ID"].strip()
        company_name = row["Company"].strip()
        if len(pnp_id) != 3:
            print(f"PNP ID: {pnp_id}", file=sys.stderr)
            continue
        if f"{pnp_id}\t{company_name}\n" not in output_lines:
            output_lines.append(f"{pnp_id}\t{company_name}\n")

    output_lines.sort(key=str.lower)

    for line in output_lines:
        args.output_file.write(line)
