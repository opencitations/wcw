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

# REQUIRED DIRECTORIES
meta_csv_output_dir = '<path>/meta_folder/csv_output/'  # INPUT DIR
citations_csv_dir = '<path>/converter_folder/citations/'  # INPUT DIR
converter_citations_csv_output_dir = '<path>/citations_folder/csv_output/'  # OUTPUT DIR
converter_citations_rdf_output_dir = '<path>/citations_folder/rdf_output/'  # OUTPUT DIR

# TRIPLESTORE and OC_OCDM
base_iri = "https://w3id.org/oc/meta/"
triplestore_url = "http://localhost:9999/blazegraph/sparql"
query_timeout = 3  # seconds
context_path = "https://w3id.org/oc/corpus/context.json"
info_dir = "<path>/meta_folder/info_dir/"
dir_split_number = 10000  # This must be multiple of the following one
items_per_file = 1000
default_dir = "_"
resp_agent = "https://w3id.org/oc/meta/prov/pa/1"
supplier_prefix = ""

# OPTIONS
rdf_output_in_chunks = True
