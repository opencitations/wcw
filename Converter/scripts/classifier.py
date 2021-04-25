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
from conf.conf import classify_even_if_type_is_uncertain
import pandas as pd


def classify_and_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is called by process(...) from run_process.py .
    It executes the classifier over the given DataFrame, which in turn
    does add a column named 'label'. Each bibliographic resource is given
    a label based on some form of heuristics.

    Here, resources that couldn't be properly classified (i.e. they have a label
    valued '?' must be dropped from the DataFrame.

    :param df: The DataFrame to be processed
    :return: The processed DataFrame
    """
    # Each entity must be classified by type
    df: pd.DataFrame = classifier(df)

    # Drop every unlabelled citation
    # This is the only place where we're going to actually delete rows
    # from the DataFrame. We keep record of them because they should
    # also be removed from the 'wiki' part of the original DataFrame.
    deleted_rows: pd.Series = df[df['label'] == '?'].index
    df = df.drop(deleted_rows, axis=0)
    df = df.reset_index(drop=True)
    return df


def classifier(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is able to classify bibliographic resources coming from the imported
    DataFrame of Wikipedia citations into one of the following labels:
    * '?' (unlabelled);
    * 'journal article';
    * 'conference paper';
    * 'book';
    * 'book part';
    * 'book chapter'.

    It uses some heuristics to predict the labels, basing its decisions exclusively on
    the available identifiers and on the column 'type_of_citation' (which represents the
    type of citation template used in Wikipedia to refer to that particular resource).

    After an initial classification step, if the 'classify_even_if_type_is_uncertain' bool
    flag is enabled in conf/conf.py, the unlabelled resources can be labelled based on their
    'type_of_citation' (when this value is meaningful).

    :param df: The DataFrame to be processed
    :return: The processed DataFrame
    """
    # Masks - for efficiency reasons, they have to be computed only once, as we do here:
    missing_doi: pd.Series = df['doi'].isna()
    existing_doi: pd.Series = ~missing_doi

    missing_isbn: pd.Series = df['isbn'].isna()
    existing_isbn: pd.Series = ~missing_isbn

    missing_pmid: pd.Series = df['pmid'].isna()
    existing_pmid: pd.Series = ~missing_pmid

    missing_pmc: pd.Series = df['pmc'].isna()
    existing_pmc: pd.Series = ~missing_pmc

    missing_issn: pd.Series = df['issn'].isna()
    existing_issn: pd.Series = ~missing_issn

    has_pubmed_identifier: pd.Series = existing_pmid | existing_pmc
    missing_pubmed_identifier: pd.Series = ~has_pubmed_identifier

    has_article_identifier: pd.Series = has_pubmed_identifier | existing_doi
    missing_article_identifier: pd.Series = ~has_article_identifier

    only_book: pd.Series = existing_isbn & missing_article_identifier

    only_isbn_and_doi: pd.Series = (
        existing_doi &
        existing_isbn &
        missing_pubmed_identifier
    )

    isbn_and_doi_book_part: pd.Series = (
        only_isbn_and_doi &
        df['type_of_citation'] == 'cite journal'
    )

    isbn_and_doi_book: pd.Series = (
        only_isbn_and_doi &
        df['type_of_citation'] == 'cite book'
    )

    is_conference_paper: pd.Series = (
        has_article_identifier &
        df['type_of_citation'] == 'cite conference'
    )

    classified_as_journal_article: pd.Series = existing_issn & \
        (has_article_identifier | (df['Periodical'].notnull() & df['Title'].notnull()))
    classified_as_conference_paper = is_conference_paper
    classified_as_book = only_book | isbn_and_doi_book
    classified_as_book_part = isbn_and_doi_book_part

    # Classification
    df['label'] = '?'
    df.loc[classified_as_journal_article, 'label'] = 'journal article'
    df.loc[classified_as_conference_paper, 'label'] = 'conference paper'
    df.loc[classified_as_book, 'label'] = 'book'
    df.loc[classified_as_book_part, 'label'] = 'book part'

    has_chapter: pd.Series = df['Chapter'].str.strip().notnull()
    book_part_with_chapter_title: pd.Series = classified_as_book_part & has_chapter
    df.loc[book_part_with_chapter_title, 'label'] = 'book chapter'

    if classify_even_if_type_is_uncertain:
        unclassified: pd.Series = df['label'] == '?'

        unclassified_journal_article: pd.Series = (
            unclassified &
            df['type_of_citation'] == 'cite journal'
        )
        unclassified_conference_paper: pd.Series = (
            unclassified &
            df['type_of_citation'] == 'cite conference'
        )
        unclassified_book: pd.Series = (
            unclassified &
            df['type_of_citation'] == 'cite book'
        )
        unclassified_book_part: pd.Series = (
            unclassified_journal_article &
            existing_isbn
        )

        df.loc[unclassified_journal_article, 'label'] = 'journal article'
        df.loc[unclassified_conference_paper, 'label'] = 'conference paper'
        df.loc[unclassified_book, 'label'] = 'book'
        df.loc[unclassified_book_part, 'label'] = 'book part'

    # Encode the 'label' column as a categorical dtype to save some memory
    # and speedup successive data manipulations:
    label_type = pd.CategoricalDtype(categories=['?',
                                                 'journal article',
                                                 'conference paper',
                                                 'book',
                                                 'book part',
                                                 'book chapter'
                                                 ], ordered=False)
    df['label'] = df['label'].astype(label_type)

    return df
