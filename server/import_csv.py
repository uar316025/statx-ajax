#!/usr/bin/env python3
"""Tool to import test result from CSV file"""
import argparse
import csv
import pathlib
import sys

from api_v1 import ADD_MODEL
from core import db


def _converting_pipe(reader, mapping):
    """Convert and map items from reader"""

    for orig_row in reader:
        row = []
        for idx, (_, conv) in zip(mapping, ADD_MODEL):
            row.append(conv(orig_row[idx]))
        yield row


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(sys.argv[0], 'Specify path to CSV file to import')

    parser.add_argument('FILE', type=pathlib.Path, help='File to import')

    res = parser.parse_args()

    # base check
    if not res.FILE.exists():
        print('Abort! File not found', res.FILE)
        return

    with open(res.FILE, 'r') as file:
        # make reader
        reader = csv.reader(file)

        columns = next(reader)

        # if first line is not header, seek to begin
        print('File first line: ' + ', '.join(columns))
        if input("Is header? y/n (default 'y') >>: ").strip().lower() not in ' y':
            file.seek(0)

        # file may contain other columns or columns in different order,
        # ask user to make columns mapping
        print('> Please enter columns order in file')
        print('Allowed:' + ', '.join(f'{idx}) {name}' for idx, (name, _) in enumerate(ADD_MODEL)))
        print('In file: ' + ', '.join(columns))
        order = input("(default '0123') >>: ") or '0123'

        # some validation
        if len(order) != len(ADD_MODEL) or not order.isdigit():
            print('Abort! Incorrect order specified!')
            return

        mapping = list(map(int, order))

        if max(mapping) >= len(columns):
            print('Abort! Order index is out of range')
            return

        # build query
        query = """
            INSERT INTO
                test_results({0})
            VALUES
                (?, ?, ?, ?);
        """.format(','.join(ADD_MODEL[idx][0] for idx in mapping))

        # insert data
        print('> Importing...')
        with db.get_conn() as conn:
            conn.executemany(query, _converting_pipe(reader, mapping))
        print('> Done...')


if __name__ == '__main__':
    main()
