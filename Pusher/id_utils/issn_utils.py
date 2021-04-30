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


def normalize_issn(issn: str) -> str:
    issn = issn.upper()
    c_list = [c for c in issn if c in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', '-'}]
    return "".join(c_list)


def issn_is_valid(issn: str) -> bool:
    if len(issn) != 9:
        return False

    if issn[4] != '-':
        return False

    if 'X' in issn[:8]:
        return False

    if '-' in issn[:4] or '-' in issn[5:]:
        return False

    tmp_issn = issn[:4] + issn[5:]
    accumulator = 0
    for i in range(8):
        accumulator += (8 - i) * digit_to_int[tmp_issn[i]]

    return accumulator % 11 == 0


def issn_check_digit(issn: str) -> str:
    tmp_issn = issn[:4] + issn[5:]
    accumulator = 0
    for i in range(7):
        accumulator += (8-i)*digit_to_int[tmp_issn[i]]

    remainder = accumulator % 11
    if remainder == 0:
        return '0'
    else:
        val = 11 - remainder
        if val == 10:
            return 'X'
        else:
            return str(val)
