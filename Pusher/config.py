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
base_iri = "https://w3id.org/oc/meta/"
query_timeout = 3  # seconds
query_wait_time = 1  # seconds
resp_agent = "https://w3id.org/oc/meta/prov/pa/3"
base_dir = "<path>/enricher_folder/rdf_output/"

pusher_citations_csv_file = "<path>/pusher_folder/citations_mapping.csv"
pusher_citations_batch_file = "<path>/pusher_folder/citations_batch.tsv"
citations_batches_dir = "<path>/citations_folder/rdf_output/"

temp_TSV_batch_output_file = "<path>/pusher_folder/temp_TSV_batch.tsv"
