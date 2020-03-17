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
        transactions = extract_text(pdf_file)
        transactions = extract_transaction_lines(transactions)


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
    lines = [{key: match.groupdict()[key].strip()
              for key in match.groupdict().keys()}
             for match in pattern.finditer(txt)]
    return lines


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
