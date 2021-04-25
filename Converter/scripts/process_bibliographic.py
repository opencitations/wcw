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
    from typing import Dict, Set

import pandas as pd

# Utils
from utils.authors_utils import stringify_authors
from utils.id_list_utils import stringify_id_list, allowed_id_schemes
from utils.utils import get_output_filepath, split_range_optional, collapse_id_list


def convert_bibliographic(df: pd.DataFrame, proc_index: int = 0) -> pd.DataFrame:
    """
    This function is able to process a DataFrame of bibliographic resources, converting it
    to a format which is compliant with the 'meta' script.

    A unique 'tmp' identifier is automatically generated and associated to each bibliographic
    resource (each row of the DataFrame).

    :param df: The Dataframe to be converted containing data about cited bibliographic resource
    :param proc_index: An integer number which identifies the process that is taking care of converting the
                        given DataFrame
    :return: The converted DataFrame
    """
    # Here we handle the 'Pages' column: its meaning can be
    # very ambiguous if the entity's macro_category is not 'article'.
    # Hence, in that case we discard its content, while in case
    # of articles we try to extract from it the begin_page and the end_page
    articles_mask: pd.Series = df['label'].isin(['journal article', 'conference paper'])
    non_articles_mask: pd.Series = ~articles_mask
    df.loc[non_articles_mask, 'Pages'] = None
    df.loc[articles_mask, 'Pages'] = df.loc[articles_mask, 'Pages'].map(split_range_optional)

    # Column 'venue' evaluation
    df['venue'] = pd.Series(dtype='object')
    is_journal: pd.Series = df['label'].isin(['journal article', 'conference paper'])

    # Swap Title and Chapter: Title <--> Chapter
    book_chapters: pd.Series = df['label'] == 'book chapter'
    df.loc[book_chapters, 'venue'] = df.loc[book_chapters, 'Title']
    df.loc[book_chapters, 'Title'] = df.loc[book_chapters, 'Chapter']

    df.loc[is_journal, 'venue'] = df.loc[is_journal, 'Periodical']

    df.drop(['Chapter', 'Periodical'], axis=1)

    # Convert column 'type_of_citation'
    wikicode_to_ocdm_mapping: Dict[str, str] = {'journal article': 'journal article',
                                                'conference paper': 'proceedings article',
                                                'book': 'book',
                                                'book part': 'book part',
                                                'book chapter': 'book chapter'
                                                }
    # df['type_of_citation'] = df['label'].map(wikicode_to_ocdm_mapping)
    df['label'] = df['label'].map(wikicode_to_ocdm_mapping)

    df = df.rename({'pmc': 'pmcid'}, axis=1)  # meta recognizes 'pmcid' instead of 'pmc'
    id_schemes: Set[str] = allowed_id_schemes.difference({'pmc'}).union({'pmcid'})

    # Stringify 'ID_list' column (enriched with 'tmp' identifiers)
    # and add identifiers to the 'venue' column where needed
    stringify_venue_identifiers(df)
    df['tmp'] = f"bib_{proc_index}_" + df.index.astype(str)  # this adds a 'tmp' column
    # The following line removes identifier columns and adds a 'ID_list' column
    df = collapse_id_list(df, 'ID_list', ['tmp', *id_schemes], do_not_drop={'tmp'})
    df['id'] = df['ID_list'].map(stringify_id_list)  # this adds an 'id'

    # Stringify 'Authors' column
    df['author'] = df['Authors'].map(stringify_authors)

    # Stringify 'Pages' column
    df['Pages'] = df['Pages'].str.join('-')

    # Add the missing column 'editor' even if we don't have data for it
    df['editor'] = None

    df = df.rename({'Title': 'title',
                    'Date': 'pub_date',
                    'Volume': 'volume',
                    'Issue': 'issue',
                    'Pages': 'page',
                    'PublisherName': 'publisher',
                    # 'type_of_citation': 'type',
                    'label': 'type'
                    }, axis=1)
    return df


def store_bibliographic(index: int, name_width: int, df: pd.DataFrame) -> None:
    """
    This function is able to store the given DataFrame as a CSV file. It's used
    to produce 'meta' compliant files inside a folder whose path is configurable
    inside conf/conf.py by modifying the 'extracted_csv_dir' string.

    Examples:
        index = 42, name_width = 4
            The output filename will be: 0042_bibliographic.csv

        index = 99, name_width = 2
            The output filename will be: 99_bibliographic.csv

    :param index: An integer number which identifies a partition of the full dataset. It's used to give
                  a recognizable name to the file
    :param name_width: How many chars should be reserved for the numeric index at the beginning of the filename
    :param df: The DataFrame to be exported as a CSV file
    """
    output_filepath: str = get_output_filepath(index, name_width, 'bibliographic')
    df.to_csv(output_filepath, index=False, chunksize=100000,
              columns=['id', 'title', 'author', 'pub_date', 'venue',
                       'volume', 'issue', 'page', 'type', 'type_of_citation', 'publisher',
                       'editor'])


def stringify_venue_identifiers(df: pd.DataFrame) -> None:
    """
    This function is able to extract identifiers that are should not be associated to the bibliographic
    resource in itself, but to its venue/container. This is done supposing that ISSNs and ISBNs associated
    to a resource internally classified as 'journal article', 'book part' or 'book chapter' should be assigned
    to their venues, rather than to them. ISBNs associated to a 'journal article' are not moved to its container
    since we cannot be sure whether that ISBN is actually referring to the article or to its container.

    :param df: The DataFrame to be processed
    """
    # Converting Pandas Series to Numpy arrays enables us to iterate far quicker over their elements:
    issn_col = df['issn'].to_numpy(copy=False)
    isbn_col = df['isbn'].to_numpy(copy=False)
    venue_col = df['venue'].to_numpy(copy=False)
    label_col = df['label'].to_numpy(copy=False)

    df_interesting: pd.Series = df[df['label'].isin(['journal article', 'book part', 'book chapter'])]
    interesting_rows = df_interesting.index.to_numpy(copy=False)

    for i in interesting_rows:
        if venue_col[i] is not None and venue_col[i].strip() != '':
            venue_id_dict = {}
            if issn_col[i] is not None:
                venue_id_dict['issn'] = issn_col[i]
                issn_col[i] = None  # remove the ID (otherwise it will be included in the collapsed 'ID_list' column)
            if isbn_col[i] is not None and label_col[i] != 'journal article':
                venue_id_dict['isbn'] = isbn_col[i]
                isbn_col[i] = None  # remove the ID (otherwise it will be included in the collapsed 'ID_list' column)
            venue_col[i] += f" [{stringify_id_list(venue_id_dict)}]"
