# !/usr/bin/python
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

import os

import pandas as pd

from conf.conf import extracted_csv_dir


def build_citations_dataframe(wiki_df: pd.DataFrame, bib_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function builds a new citations DataFrame containing only two columns, one for the 'tmp'
    identifier of the 'citing' Wikipedia page and the other for the 'tmp' identifier of the
    'cited' bibliographic resource. The given DataFrames must have the same number of rows.

    Wikipedia pages and bibliographic resources are paired based on their row index in the respective
    DataFrames.

    :param wiki_df: The DataFrame of Wikipedia pages
    :param bib_df: The DataFrame of bibliographic resources
    :return: The new citations DataFrame that contains only two columns: 'citing' and 'cited'
    """
    df = pd.DataFrame()
    df['citing'] = wiki_df['tmp']
    df['cited'] = bib_df['tmp']
    return df


def store_citations(index: int, name_width: int, df: pd.DataFrame) -> None:
    """
    This function is able to store the given DataFrame as a CSV file. It's used
    to produce a temporary file needed by the run_process_citations.py script.
    The output directory is configurable inside conf/conf.py by modifying the
    'extracted_csv_dir' string: the actual output path will be 'extracted_csv_dir' + '/citations'.

    Examples:
        index = 42, name_width = 4
        The output filename will be: citations/0042.csv

        index = 99, name_width = 2
        The output filename will be: citations/99.csv

    :param index: An integer number which identifies a partition of the full dataset. It's used to give
                  a recognizable name to the file
    :param name_width: How many chars should be reserved for the numeric index at the beginning of the filename
    :param df: The DataFrame to be exported as a CSV file
    """
    subfolder_name: str = str(index).rjust(name_width, '0')
    citations_dir: str = os.path.join(extracted_csv_dir, 'citations')
    if not os.path.exists(citations_dir):
        os.mkdir(citations_dir)

    output_filepath: str = citations_dir + os.sep + subfolder_name + '.csv'
    df.to_csv(output_filepath, index=False, chunksize=100000,
              columns=['citing', 'cited'])
