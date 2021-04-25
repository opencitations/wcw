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
    import pandas as pd

# Utils
from utils.id_list_utils import stringify_id_list
from utils.utils import get_output_filepath, collapse_id_list


def convert_wiki(df: pd.DataFrame, proc_index: int = 0) -> pd.DataFrame:
    """
    This function is able to process a DataFrame of Wikipedia pages, converting it
    to a format which is compliant with the 'meta' script.

    A unique 'tmp' identifier is automatically generated and associated to each Wikipedia
    page (each row of the DataFrame).

    :param df: The Dataframe to be converted containing data about citing Wikipedia pages
    :param proc_index: An integer number which identifies the process that is taking care of converting the
                        given DataFrame
    :return: The converted DataFrame
    """
    # Convert column 'id' and add the 'tmp' ID:
    df['tmp'] = f"wiki_{proc_index}_" + df.index.astype(str)  # this adds a 'tmp'

    df = df.rename({'id': 'wikipedia'}, axis=1)
    # In our case, no NaN values can be found inside this column: this means that we can safely convert
    # its content from floats to strings without obtaining any 'nan' or 'None' value.
    df['wikipedia'] = df['wikipedia'].astype(str)

    # The following line removes the 'wikipedia' column and adds an 'ID_list' column
    df = collapse_id_list(df, 'ID_list', ['tmp', 'wikipedia'], do_not_drop={'tmp'})
    df['ID_list'] = df['ID_list'].map(stringify_id_list)  # this adds an 'id'

    df = df.rename({'page_title': 'title',
                    'ID_list': 'id'
                    }, axis=1)

    df['author'] = None  # not applicable
    df['pub_date'] = None  # not applicable
    df['venue'] = None  # not applicable
    df['volume'] = None  # not applicable
    df['issue'] = None  # not applicable
    df['page'] = None  # not applicable
    df['type'] = None  # OCDM doesn't provide support for web resources
    df['publisher'] = None  # not applicable
    df['editor'] = None  # not known, it could be a very long list of usernames...

    return df


def store_wiki(index: int, name_width: int, df: pd.DataFrame) -> None:
    """
    This function is able to store the given DataFrame as a CSV file. It's used
    to produce 'meta' compliant files inside a folder whose path is configurable
    inside conf/conf.py by modifying the 'extracted_csv_dir' string.

    Examples:
        index = 42, name_width = 4
            The output filename will be: 0042_wiki.csv

        index = 99, name_width = 2
            The output filename will be: 99_wiki.csv

    :param index: An integer number which identifies a partition of the full dataset. It's used to give
                  a recognizable name to the file
    :param name_width: How many chars should be reserved for the numeric index at the beginning of the filename
    :param df: The DataFrame to be exported as a CSV file
    """
    output_filepath: str = get_output_filepath(index, name_width, 'wiki')
    df.to_csv(output_filepath, index=False, chunksize=100000,
              columns=['id', 'title', 'author', 'pub_date', 'venue',
                       'volume', 'issue', 'page', 'type', 'publisher',
                       'editor'])
