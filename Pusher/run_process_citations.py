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
    from typing import Dict, List, Optional

from rdflib import URIRef, Graph

import glob
import csv
from config import citations_batches_dir, pusher_citations_csv_file, base_iri, resp_agent, pusher_citations_batch_file
from oc_ocdm import Reader
from oc_ocdm.graph import GraphSet


def store_batch(statements: List[str]):
    """
    This function appends a given list of statements to the output
    TSV QuickStatements citations batch file.

    :param statements: A list of TSV QuickStatements statements
    """
    with open(pusher_citations_batch_file, 'a', encoding='utf-8') as f:
        f.write('\n'.join(statements))


def process_chunk(chunk_filepath: str, citations_mapping: Dict[URIRef, str]):
    """
    This function handles all the steps which are needed to fully process a single
    chunk of the citations input dataset.
      - Firstly, the RDF graph serialized inside the chunk file
        is imported in the form of an oc_ocdm's GraphSet.
      - Secondly, a loop over each CI entity
        is performed: the citing and cited OCDM IRIs are extracted and then mapped
        to the Wikidata IDs contained inside the given mapping dictionary (when possible).
        A TSV statement is created for each citation to be uploaded.
      - Lastly, the collected list of statements is appended to the output file.

    :param chunk_filepath: A string representing the filesystem path to the chunk to be imported
    :param citations_mapping: A dictionary mapping OCDM IRIs into the corresponding Wikidata IDs
    """
    # PROCESS INITIALIZATION
    statements: List[str] = []

    # DATA IMPORT PHASE
    graph_chunk: Graph = Graph().parse(location=chunk_filepath, format='nt11')

    g_set: GraphSet = GraphSet(base_iri, wanted_label=False)
    Reader.import_entities_from_graph(g_set, graph_chunk, resp_agent, enable_validation=False)

    # TSV STATEMENTS GENERATION
    for ci in g_set.get_ci():
        citing_uri: Optional[URIRef] = ci.get_citing_entity().res
        cited_uri: Optional[URIRef] = ci.get_cited_entity().res

        if citing_uri in citations_mapping and cited_uri in citations_mapping:
            citing_qid: str = citations_mapping[citing_uri]
            cited_qid: str = citations_mapping[cited_uri]
            statements.append(f'{citing_qid}\tP2860\t{cited_qid}\tS248\tQ328')

    # TSV STATEMENTS EXPORT
    store_batch(statements)


"""
Entry point of the run_process_citations.py script.
This process is supposed to be executed after the run_process.py script.
It's responsible for the bulk-upload of citations between Wikipedia pages
and bibliographic resources. Citations are extracted from the output RDF files
of the Converter scripts (citations chunk files are left untouched by the Enricher
scripts).
"""
if __name__ == '__main__':
    files: List[str] = glob.glob(citations_batches_dir + "*.nt", recursive=False)
    if len(files) <= 0:
        print("No file to be processed. Terminating the process...")
    else:
        print(f"{len(files)} files to be processed. Please wait...")
        print("START")

        # We first have to reconstruct a mapping dictionary from CSV files exported
        # by the run_process.py script.
        ocdm_to_wikidata: Dict[URIRef, str] = {}
        with open(pusher_citations_csv_file, 'r') as csvfile:
            reader: csv.DictReader = csv.DictReader(csvfile, fieldnames=['ocdm_uri', 'wikidata_qid'])
            for row in reader:
                key: URIRef = URIRef(row['ocdm_uri'])
                value: str = row['wikidata_qid']
                ocdm_to_wikidata[key] = value

        # Each input files must be processed sequentially:
        for file in files:
            process_chunk(file, ocdm_to_wikidata)

        print("The process terminated successfully. Please, manually bulk-upload the TSV")
        print(f"QuickStatements file which is available at this location: {pusher_citations_batch_file}")
        print("END")
