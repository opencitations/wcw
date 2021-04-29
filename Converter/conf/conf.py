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

# PERFORMANCE OPTIONS
parquet_engine = 'pyarrow'  # ['pyarrow', 'fastparquet' 'auto']
process_pool_size = 0  # '0' for automatic choice based on actual CPU cores count, '1' for sequential processing

# Some citations do not have any ID that can help us
# classifying them (i.e. doi, pmid, isbn, ...). Should
# the script try to label them based on the 'type_of_citation' column?
# At the end of the classification process, unlabelled
# citations will be discarded.
classify_even_if_type_is_uncertain = True

# REQUIRED DIRECTORIES
input_parquet_file = '<path>/dataset.parquet'
extracted_csv_dir = '<path>/converter_folder/'

# CONVERSION OPTIONS
allowed_citation_types = {'citation',  # generic citation: to be further examined
                          'cite book',  # book
                          'cite conference',  # conference paper
                          'cite journal',  # academic journals
                          'cite arxiv',  # ArXiv preprint
                          'cite biorxiv',  # BioRxiv preprint
                          'cite ssrn',  # SSRN paper
                          'cite magazine',  # magazine, periodical
                          }
