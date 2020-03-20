#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HSBC credit card statement PDF to CSV converter.
"""


import argparse
import glob
import re
import math
import pdfplumber
import csv


class PayByTxnError(Exception):
    pass


def main():
    args = parse_args()
    pdf_files = glob.glob(args.input)
    for _, pdf_file in enumerate(pdf_files):
        text = extract_text(pdf_file)
        stmt_date = get_stmt_date(text)
        debit_value = get_debit_value(text)
        transactions = extract_transaction_lines(text)
        transactions = strip_spaces(transactions)
        transactions = remove_paid_txns(transactions)
        transactions = string2float(transactions)
        transactions = change_date_fmt(transactions, stmt_date)
        transactions = sort_txnx(transactions)
        total_amount = get_total_amount(transactions)
        if math.isclose(debit_value, total_amount, abs_tol=0.001):
            pass
        else:
            print('Error! Total amount of new transactions does not '
                  'match to be debited amount.')
            print(f'sum new transactions = {total_amount:,.2f}')
            print(f'amount to be debited = {debit_value}')
            break
        save_to_csv(transactions, pdf_file)


def get_stmt_date(text):
    months = r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
    pattern = re.compile(
        r'(?<=Statement Date  )[0-9]{2}' + months + r'[0-9]{4}',
        re.MULTILINE)
    return pattern.search(text)[0]


def get_debit_value(text):
    pattern = re.compile(
        r'(?<=Your specified account will be debited '
        r'for AED )[0-9]*,?[0-9]+\.[0-9]{2}',
        re.MULTILINE)
    debit_value = -1 * float(pattern.search(text)[0].replace(',', ''))
    return debit_value


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


def remove_paid_txns(transactions):
    """
    Remove all credit card balance payments.
    """
    paid_txns = [idx for idx, txn in enumerate(transactions)
                 if txn['TransactionDetails'].find('PAY BY 036-288942-001') >= 0 and \
                txn['Amount'][-2:] == 'CR']
    if len(paid_txns) == 0:
        raise PayByTxnError('\'PAY BY\' transaction(s) not found. '
                            'At least one transaction expected.')
    for idx in paid_txns:
        del transactions[idx]
    return transactions


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


def change_date_fmt(transactions, stmt_date):
    mmap = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}
    stmt_month = stmt_date[-7:-4]
    stmt_year = int(stmt_date[-4:])
    for idx, txn in enumerate(transactions):
        post_day = txn['PostingDate'][:2]
        post_month= txn['PostingDate'][-3:]
        if stmt_month == 'JAN' and post_month == 'DEC':
            txn['PostingDate'] = f'{post_day}/{mmap[post_month]}/{stmt_year - 1}'
        else:
            txn['PostingDate'] = f'{post_day}/{mmap[post_month]}/{stmt_year}'
        txn_day = txn['TransactionDate'][:2]
        txn_month= txn['TransactionDate'][-3:]
        if stmt_month == 'JAN' and txn_month == 'DEC':
            txn['TransactionDate'] = f'{txn_day}/{mmap[txn_month]}/{stmt_year - 1}'
        else:
            txn['TransactionDate'] = f'{txn_day}/{mmap[txn_month]}/{stmt_year}'
        transactions[idx] = txn
    return transactions


def sort_txnx(transactions):
    """ Sort list of transactions by 'PostingDate'. """
    transactions = sorted(transactions, key=sort_by_date)
    return transactions


def sort_by_date(item):
    """ Sorting function for sorted() function. """
    date_parts = item['PostingDate'].split('/')
    day = date_parts[0]
    month = date_parts[1]
    year = date_parts[2]
    return year, month, day


def get_total_amount(transactions):
    amount = sum([txn['Amount'] for txn in transactions])
    return amount


def save_to_csv(transactions, pdf_file):
    print()
    print(f'processing transactions from file \'{pdf_file}\'')
    print()
    csv_file_name = pdf_file[:pdf_file.rfind('.')] + '.csv'
    file = open(csv_file_name, 'w', newline='')
    csv_file = csv.writer(file, delimiter=';')
    for idx, txn in enumerate(transactions):
        print('---------------------------------------------------------------')
        print('transaction number : ' + str(idx + 1))
        print('posting date       : ' + txn['PostingDate'])
        print('transaction date   : ' + txn['TransactionDate'])
        print('transaction details: ' + txn['TransactionDetails'])
        print('amount             : ' + str(txn['Amount']))
        row = [txn['PostingDate'],
               txn['TransactionDate'],
               txn['TransactionDetails'],
               str(txn['Amount'])]
        csv_file.writerow(row)
    file.close()


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
