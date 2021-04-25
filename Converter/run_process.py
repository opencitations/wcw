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
    from typing import Tuple, List
    import pandas as pd

import glob
import os
import multiprocessing
import time

from scripts.classifier import classify_and_filter
from scripts.reader import read_partition
from conf.conf import input_parquet_file, process_pool_size, extracted_csv_dir

# Utils
from utils.authors_utils import parse_authors
from utils.id_list_utils import parse_id_list
from utils.utils import explode_id_list, remove_forbidden_chars

# Converters and Storers
from scripts.process_bibliographic import convert_bibliographic, store_bibliographic
from scripts.process_wiki import convert_wiki, store_wiki
from scripts.process_citations import build_citations_dataframe, store_citations


def split_by_wikipedia_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function splits the given DataFrame by separating columns related
    to the citing Wikipedia page from the rest.

    :params df: The DataFrame to be split
    """
    wiki_columns: List[str] = ['page_title', 'id']
    wiki_df = df[wiki_columns].copy(deep=True)
    bibliographic_df = df.drop(wiki_columns, axis=1)
    return wiki_df, bibliographic_df


def process(arg: Tuple[int, int, str]) -> None:
    """
    This function takes care of the entire processing of a single parquet
    partition file. Data is imported into a Pandas DataFrame in which each
    row contains information about a particular citation extracted from an
    enwiki dump by the Extractor. Since there are both columns related to the
    citing Wikipedia page and to the cited bibliographic resource, the DataFrame
    is split in two: 'convert_bibliographic()' and 'convert_wiki' will handle
    the two different conversions.

    The end goal of this function is that of converting the parquet partition
    files into CSV files which are compliant with the 'meta' script. This will
    allow 'meta' to digest the output CSV files one by one and to produce an
    OpenCitations compliant RDF graph.

    During the process, both columns and rows are filtered out from the DataFrames
    in the case of too dirty data or of data which is of no bibliographical interest.

    Furthermore, a citations DataFrame is created and stored as a CSV file. This will
    be needed by the run_process_citations.py script for it to be able to generate
    a proper OpenCitations RDF graph of citations.

    :param arg: A tuple containing the name_width (i.e. the required length of the
                output filenames), the proc_index (i.e. an incremental integer index
                which differentiates every spawned process) and the input_file (i.e.
                the path of the input parquet partition file)
    """
    p_start: float = time.time()

    # 'arg' is a tuple and it must be exploded as follows:
    name_width, proc_index, input_file = arg

    df = read_partition(input_file)
    df = remove_forbidden_chars(df)

    # First of all, we need to parse structured data for a more convenient
    # access to the information contained in it.
    df['Authors'] = df['Authors'].astype(str).map(parse_authors)
    df['ID_list'] = df['ID_list'].astype(str).map(parse_id_list)
    df = explode_id_list(df, 'ID_list')  # this creates a lot of additional columns, removing 'ID_list'

    df = classify_and_filter(df)

    # The initial DataFrame is split in two parts:
    wiki_df, bibliographic_df = split_by_wikipedia_columns(df)

    # Produce all the needed dataframes
    bibliographic_df = convert_bibliographic(bibliographic_df, proc_index)
    wiki_df = convert_wiki(wiki_df, proc_index)
    citations_df = build_citations_dataframe(wiki_df, bibliographic_df)

    # Store all the dataframes
    store_bibliographic(proc_index, name_width, bibliographic_df)
    store_wiki(proc_index, name_width, wiki_df)
    store_citations(proc_index, name_width, citations_df)

    p_end: float = time.time()
    print(f"Process {proc_index} took ~{round(p_end - p_start, 2)}s")


""" Entry point of the run_process.py script.
This process is supposed to import data from the parquet dataset coming from the Extractor,
filter and clean it as much as possible and finally exporting it in a CSV file compliant
with the 'meta' package (which will take care of converting the data inside the CSV file into
an RDF graph following the OCDM specifications).
the output files of the Enricher scripts. Along with their reconciliation,
entities are converted into the Wikidata's data-model and finally bulk-uploaded
through the use of QuickStatements.
"""
if __name__ == '__main__':
    print("START")

    start = time.time()
    # Removing trailing file separators:
    while input_parquet_file[-1] == os.sep:
        parquet_dir = input_parquet_file[:-1]
    while extracted_csv_dir[-1] == os.sep:
        output_dir = extracted_csv_dir[:-1]

    # Apply default value for 'process_pool_size':
    if process_pool_size is None or process_pool_size <= 0:
        process_pool_size = multiprocessing.cpu_count()

    # The parquet file is partitioned into several
    # files. The Converter step will be applied to
    # each of them, with the level of parallelism
    # defined by the value of 'process_pool_size':
    part_list = glob.glob(input_parquet_file + os.sep + 'part*.parquet')
    partition_number = len(part_list)
    filename_width = len(str(partition_number))

    # Here the arguments for each parallel process are prepared:
    proc_arguments = []
    for i in range(partition_number):
        # For each process that has to be spawned, append its arguments
        proc_arguments.append((filename_width, i, part_list[i]))

    # Pool must be called with maxtasksperchild=1 so that each process can
    # be cleared out once it has completed its task. This avoids huge memory leaks.
    ctx = multiprocessing.get_context('spawn')
    with ctx.Pool(process_pool_size, maxtasksperchild=1) as pool:
        pool.map(process, proc_arguments)
    end = time.time()
    print("END %d seconds elapsed." % (end - start))
