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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Tuple, List, Set, Match

import os
import re
import pandas as pd

from conf.conf import extracted_csv_dir


def get_output_filepath(index: int, folder_name_width: int, filename: str) -> str:
    subfolder_name: str = str(index).rjust(folder_name_width, '0')
    if not os.path.exists(extracted_csv_dir):
        os.mkdir(extracted_csv_dir)
    return extracted_csv_dir + os.sep + subfolder_name + '_' + filename + '.csv'


split_range_regex = r"^[^0-9iIvVxXlLcCdDmM]*([1-9][0-9]*)\s*[\-‐–—−‑⁃­‒]+\s*([1-9][0-9]*)[^0-9iIvVxXlLcCdDmM]*$"
#                 [no arabic or roman digits]  (start_page)   [separators]     (end_page)  [no arabic or roman digits]


def split_range(s: str) -> Tuple[str, str]:
    if s is None:
        return '', ''

    match: Match = re.match(split_range_regex, s, re.UNICODE)
    if match is not None:
        start_page: str = match.group(1)
        end_page: str = match.group(2)
        len_start: int = len(start_page)
        len_end: int = len(end_page)
        if len_start == len_end:
            if int(start_page) <= int(end_page):
                return start_page, end_page
            else:
                return '', ''
        elif len_start < len_end:
            return start_page, end_page
        else:
            # len_start > len_end
            start_page_first_part: str = start_page[:-len_end]
            start_page_second_part: str = start_page[-len_end:]
            if int(start_page_second_part) < int(end_page):
                # For example: '170-85' becomes '170-185'
                return start_page, (start_page_first_part + end_page)
            else:
                return '', ''
    else:
        return '', ''


def split_range_optional(s: str) -> Optional[Tuple[str, str]]:
    start, end = split_range(s)
    if start == "" or end == "":
        return None
    else:
        return start, end


def explode_id_list(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    df = df.join(pd.DataFrame(df.pop(column_name).to_list()))
    return df


def collapse_id_list(df: pd.DataFrame, new_column: str, columns: List[str],
                     do_not_drop: Set[str] = None) -> pd.DataFrame:
    df[new_column] = df[columns].to_dict(orient='records')

    to_be_dropped: List[str] = [col for col in columns if col not in do_not_drop]
    df = df.drop(to_be_dropped, axis=1)
    return df


def remove_forbidden_chars(df: pd.DataFrame) -> pd.DataFrame:
    forbidden_chars: Set[str] = {'[', ']'}
    columns_to_be_cleaned: List[str] = ['Chapter', 'Periodical', 'PublisherName', 'Title', 'page_title']

    for column in columns_to_be_cleaned:
        for char in forbidden_chars:
            df[column] = df[column].str.replace(char, '', regex=False)

    # 'Authors' and 'ID_list' columns also needs the removal of some forbidden characters.
    # This is done respectively inside the 'stringify_authors' and 'stringify_id_list'
    # methods, since these particular columns contain structured data that needs to
    # be handled in a specific way.

    return df
