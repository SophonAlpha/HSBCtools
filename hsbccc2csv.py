#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HSBC credit card statement PDF to CSV converter.
"""


import argparse
import glob
import pdfplumber


def main():
    args = parse_args()
    pdf_files = glob.glob(args.input)
    for _, pdf_file in enumerate(pdf_files):
        convert(pdf_file)


def convert(pdf_file):
    pdf = pdfplumber.open(pdf_file)
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
    regex = '(?P<PostingDate>[0-9]{2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC) )(?P<TransactionDate>[0-9]{2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC) )(?P<TransactionDetails>.+)(?P<Amount> [0-9]+,?[0-9]*\.[0-9]{2} {0,2}(CR)*$)'



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
