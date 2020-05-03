#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Transform HSBC current account CSV exports for import into WISO Mein Geld.
"""

import argparse
import glob
import re
import os.path


def main():
    """
    Main function. Process all PDF files submitted via command line parameter.
    """
    args = parse_args()
    csv_files = glob.glob(args.input)
    if csv_files:
        for csv_file in csv_files:
            process_csv_file(csv_file)
    else:
        print(f'Can not find file(s) \'{args.input}\'')


def process_csv_file(csv_file):
    """
    Process a single CSV file.
    """
    print()
    print(f'processing transactions from file \'{csv_file}\'')
    print()
    txns = open(csv_file, 'r').read()
    txns = remove_funny_chars(txns)
    txns = remove_commas(txns)
    txns = remove_quotation_marks(txns)
    txns = comma_to_semicolon(txns)
    txns = dot_to_comma(txns)
    txns = remove_excessive_spaces(txns)
    save_csv(txns, csv_file)
    print()


def remove_funny_chars(txns):
    """
    There are some funny characters at the beginning of the CSV file exported
    from the HSBC online banking website. We will delete them.
    """
    pattern = re.compile(r'^.+(?=[0-9]{2}\/[0-9]{2}\/[0-9]{4})', re.MULTILINE)
    txns = pattern.sub('', txns)
    return txns


def remove_commas(txns):
    """
    Remove the thousand separator commas.
    """
    pattern = re.compile(r'(?<=[0-9]),(?=[0-9]{1,3})', re.MULTILINE)
    txns = pattern.sub('', txns)
    return txns


def remove_quotation_marks(txns):
    """
    Remove quotation marks
    """
    return txns.replace('"', '')


def comma_to_semicolon(txns):
    """
    Replace the comma with semicolon as separator between the columns.
    """
    return txns.replace(',', ';')


def dot_to_comma(txns):
    """
    Convert the decimal separator dots to commas. This is required to import
    the transactions to WISO Mein Geld.
    """
    pattern = re.compile(r'\.(?=[0-9]{2}[;\n])', re.MULTILINE)
    txns = pattern.sub(',', txns)
    return txns


def remove_excessive_spaces(txns):
    """
    Remove excessive spaces.
    """
    pattern = re.compile(r' {2,}', re.MULTILINE)
    txns = pattern.sub(' ', txns)
    return txns


def sort_txnx(transactions):
    """
    Sort list of transactions by 'PostingDate'.
    """
    transactions = sorted(transactions, key=sort_by_date)
    return transactions


def sort_by_date(item):
    """
    Sorting function for sorted() function.
    """
    date_parts = item['PostingDate'].split('/')
    day = date_parts[0]
    month = date_parts[1]
    year = date_parts[2]
    return year, month, day


def save_csv(txns, csv_file):
    """
    Save extracted credit card transactions to CSV file.
    """
    csv_file_name = csv_file[:csv_file.rfind('.')] + '_transformed' + '.csv'
    file = open(csv_file_name, 'w', newline='')
    file.write(txns)
    file.close()


def parse_args():
    """
    Parse the arguments submitted with the script.
    """
    parser = argparse.ArgumentParser(
        description='Transform HSBC current account CSV exports for import '
                    'into WISO Main Geld.')
    parser.add_argument('-i', '--input', type=str,
                        help='Path to CSV files to be transformed.')
    return parser.parse_args()


if __name__ == '__main__':
    main()
