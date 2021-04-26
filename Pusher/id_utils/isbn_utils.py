#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Simone Persiani <iosonopersia@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.
from __future__ import annotations
digit_to_int = {'0': 0,
                '1': 1,
                '2': 2,
                '3': 3,
                '4': 4,
                '5': 5,
                '6': 6,
                '7': 7,
                '8': 8,
                '9': 9,
                'X': 10
                }


def isbn_normalize(isbn: str):
    isbn = isbn.upper()
    c_list = [c for c in isbn if c in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', '-'}]
    isbn = "".join(c_list)

    # We must do the following checks because we choose to allow '-' chars inside the ISBN string
    # (but not at the start nor the end of the string)...
    while isbn[-1] == '-':
        isbn = isbn[:-1]
    while isbn[0] == '-':
        isbn = isbn[1:]
    return isbn


def isbn_length(isbn: str):
    isbn = isbn.upper()

    count = 0
    for c in isbn:
        if c in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X'}:
            count += 1

    return count


def isbn10_is_valid(isbn10):
    isbn10 = isbn10.replace('-', '')
    if len(isbn10) != 10:
        return False

    t = 0
    s = 0
    for i in range(0, 10):
        t += digit_to_int[isbn10[i]]
        s += t

    return s % 11 == 0


def isbn10_check_digit(isbn10):
    isbn10 = isbn10.replace('-', '')

    s = 0
    for i in range(9):
        s += (10-i)*digit_to_int[isbn10[i]]
    val = (11 - (s % 11)) % 11
    if val == 10:
        return 'X'
    else:
        return str(val)


def from_isbn10_to_isbn13(isbn10):
    isbn13 = '978-' + isbn10
    isbn13 = isbn13[:-1] + isbn13_check_digit(isbn13)
    return isbn13


def isbn13_is_valid(isbn13):
    isbn13 = isbn13.replace('-', '')
    if len(isbn13) != 13:
        return False

    if 'X' in isbn13:
        return False

    coefficients = [1, 3] * 6 + [1]
    accumulator = 0
    for i in range(0, 13):
        accumulator += coefficients[i]*digit_to_int[isbn13[i]]

    return accumulator % 10 == 0


def isbn13_check_digit(isbn13):
    isbn13 = isbn13.replace('-', '')

    coefficients = [1, 3] * 6
    s = 0
    for i in range(12):
        s += coefficients[i]*digit_to_int[isbn13[i]]
    val = 10 - (s % 10)
    return str(val)


def from_isbn13_to_isbn10(isbn13):
    if isbn13[:3] == '978':
        isbn10 = isbn13[3:]
        while isbn10[0] == '-':
            isbn10 = isbn10[1:]
        isbn10 = isbn10[:-1] + isbn10_check_digit(isbn10)
        return isbn10
    else:
        return None
