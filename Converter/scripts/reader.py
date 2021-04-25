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
import pandas as pd
from conf.conf import parquet_engine, allowed_citation_types

"""
all_columns = {'AccessDate',  'Chapter', 'Chron', 'City', 'Date', 'Degree',
               'Edition', 'Encyclopedia', 'Format', 'ID_list', 'Issue', 'Pages',
               'Periodical', 'PublicationPlace', 'PublisherName', 'Series',
               'SeriesNumber', 'Title', 'TitleType', 'URL', 'Volume', 'citations',
               'id', 'page_title', 'r_id', 'r_parentid', 'sections',
               'type_of_citation', 'metadata_file', 'updated_identifier',
               'conf_score'}
"""
columns_to_be_imported = ['Authors', 'Chapter', 'Date', 'ID_list', 'Issue', 'Pages',
                          'Periodical', 'PublisherName', 'Title', 'Volume', 'id',
                          'page_title', 'type_of_citation']

unicode_escaped_columns = ['Authors', 'Chapter', 'Date', 'ID_list', 'Issue', 'Pages',
                           'Periodical', 'PublisherName', 'Title', 'Volume']


def read_partition(filepath: str) -> pd.DataFrame:
    """
    This function is needed to import a parquet partition file into a Pandas DataFrame.
    Because of the way parquet files are formatted, it's easy to speed up the import
    process just by reading into memory only a subset of the available columns.

    Pandas supports two different engines for parquet files reading: both pyarrow and fastparquet,
    with the former being warmly suggested by the authors of this work. The engine can be chosen
    by properly configuring a parameter inside the conf.py file.

    As an additional constraint, a filter on the value of the 'Title' column is established:
    in case of parsing errors, the Extractor script creates rows with a 'Title' equal to
    'Citation generic template not possible'. Should this behaviour be changed in the future,
    this function would have to be updated consequently.

    Some columns contain strings that are badly formatted: they contain unicode escape sequences
    instead of the corresponding unicode chars. This is fixed here before returning the DataFrame.

    :param filepath: The path of the parquet partition file to be imported
    """
    arguments = {'columns': columns_to_be_imported,
                 'filters': []
                 }

    # In case of non parseable citation templates, the Extractor outputs
    # the 'Title' column value as 'Citation generic template not possible'
    non_parseable_constraint = ('Title', '!=', 'Citation generic template not possible')

    for cit_type in allowed_citation_types:
        # Filtering constraints are expressed in DNF (Disjunction Normal Form)
        arguments['filters'].append([non_parseable_constraint, ('type_of_citation', '=', cit_type)])

    if parquet_engine is not None and parquet_engine != 'auto':
        if parquet_engine == 'pyarrow':
            arguments['use_threads'] = True

        df = pd.read_parquet(filepath, engine=parquet_engine, **arguments)
    else:
        df = pd.read_parquet(filepath, engine='auto', **arguments)

    # String charsets are unified. Every string will be internally
    # stored and handled as a unicode string.
    for col in unicode_escaped_columns:
        df[col] = df[col].str.decode('unicode-escape', errors='strict')

    return df
