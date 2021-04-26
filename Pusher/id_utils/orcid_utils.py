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


def normalize_orcid(orcid: str) -> str:
    orcid = orcid.upper()
    c_list = [c for c in orcid if c in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', '-'}]
    return "".join(c_list)


def orcid_is_valid(orcid: str) -> bool:
    if len(orcid) != 19:
        return False

    if orcid[4] != '-' or orcid[9] != '-' or orcid[14] != '-':
        return False

    if 'X' in orcid[:18]:
        return False

    if '-' in orcid[:4] or '-' in orcid[5:9] or '-' in orcid[10:14] or '-' in orcid[15:]:
        return False

    check_digit = orcid_check_digit(orcid)
    return orcid[-1] == check_digit


def orcid_check_digit(orcid: str) -> str:
    tmp_orcid = orcid[:4] + orcid[5:9] + orcid[10:14] + orcid[15:]
    accumulator = 0
    for i in range(15):
        accumulator = (accumulator + digit_to_int[tmp_orcid[i]]) * 2

    remainder = accumulator % 11
    result = (12 - remainder) % 11
    if result == 10:
        return 'X'
    else:
        return str(result)
