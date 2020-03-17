#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HSBC credit card statement PDF to CSV converter.
"""


import argparse
import glob
import re
import pdfplumber


def main():
    args = parse_args()
    pdf_files = glob.glob(args.input)
    for _, pdf_file in enumerate(pdf_files):
        text = extract_text(pdf_file)
        stmt_date = get_stmt_date(text)
        transactions = extract_transaction_lines(text)
        transactions = strip_spaces(transactions)
        transactions = string2float(transactions)
        transactions = change_date_fmt(transactions, stmt_date)


def get_stmt_date(text):
    months = r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
    pattern = re.compile(
        r'(?<=Statement Date  )[0-9]{2}' + months + r'[0-9]{4}',
        re.MULTILINE)
    return pattern.search(text)[0]


def extract_text(pdf_file):
    pdf = pdfplumber.open(pdf_file)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    return text


def extract_transaction_lines(txt):
    months = r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
    pattern = re.compile(
        r'(?P<PostingDate>[0-9]{2}' + months + r' )' + \
        r'(?P<TransactionDate>[0-9]{2}' + months + r' )' + \
        r'(?P<TransactionDetails>.+)' + \
        r'(?P<Amount> [0-9]+,?[0-9]*\.[0-9]{2} {0,2}(CR)*$)',
        re.MULTILINE)
    lines = [match.groupdict() for match in pattern.finditer(txt)]
    return lines


def strip_spaces(lines):
    lines = [{key: line[key].strip() for key in line.keys()}
             for line in lines]
    return lines


def string2float(transactions):
    txns_updated = []
    for txn in transactions:
        txn['Amount'] = -1 * float(txn['Amount'].replace(',', ''))\
            if txn['Amount'][-2:] != 'CR' \
            else float(txn['Amount'][:-2].replace(',', ''))
        txns_updated.append(txn)
    return txns_updated


def change_date_fmt(transactions):
    txns_updated = []
    for txn in transactions:
        # txn['PostingDate'] =
        # txn['TransactionDate'] =

        txns_updated.append(txn)
    return txns_updated


def parse_args():
    """
    Parse the arguments submitted with the script.
    """
    parser = argparse.ArgumentParser(
        description='Convert HSBC credit card statements from PDF to CSV.')
    parser.add_argument('-i', '--input', type=str,
                        help='Path to PDF files to be converted.')
    return parser.parse_args()


if __name__ == '__main__':
    main()
