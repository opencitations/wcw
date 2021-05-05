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
    from typing import List, Dict, Optional
    from rdflib import URIRef
    from oc_ocdm.graph.entities import Identifier

import glob
import os

from oc_ocdm import Reader
from oc_ocdm.graph import GraphSet
from oc_ocdm.graph.entities.bibliographic import BibliographicResource

from rdflib import Graph, Namespace
from config import base_iri, resp_agent, base_dir, pusher_citations_csv_file

from process_bibliographic_resource import process_bibliographic_resource
from process_wikipedia_page import process_wikipedia_page
from reconciliator import Reconciliator
from uploader import upload_batch
from entities.WDEntity import WDEntity
from entities.EnWikiPageWDEntity import EnWikiPageWDEntity


def is_wikipedia_page(br: BibliographicResource) -> bool:
    """
    This predicate can be used to discover whether a BR (BibliographicResource)
    entity actually represents a Wikipedia page or not. It looks for
    the presence of an associated ID (Identifier) with the datacite:wikipedia schema.

    :param br: The BR entity to be checked
    :return: True if the BR entity is a Wikipedia page, False otherwise
    """
    datacite: Namespace = Namespace('http://purl.org/spar/datacite/')
    id_list: List[Identifier] = br.get_identifiers()
    wikipedia_found: bool = False
    for identifier in id_list:
        id_scheme: Optional[URIRef] = identifier.get_scheme()
        if id_scheme == datacite.wikipedia:
            wikipedia_found = True
            break
    return wikipedia_found


def store_citations_csv_file(second_batch: Dict[URIRef, WDEntity]):
    """
    This function stores a temporary CSV file consisting of one row for each properly
    reconciled WDEntity belonging to the given batch. The first column contains the OCDM IRI
    of the entities, while their corresponding Wikidata ID is stored in the second one.

    It's supposed to be called after a chunk has been fully processed, since
    at that time all reconciliations will have taken place and hopefully the Wikidata
    ID of all the entities will be known.

    The produced CSV file will be read as input by the run_process_citations.py script,
    which will effectively create citations between the Wikidata entities uploaded by
    the run_process.py script.

    PLEASE NOTE: maybe some entity QIDs needed by the run_process_citations.py script could
    be present inside the reconciliator._matches dictionary and not inside the 'second_batch'
    argument (for example those entities that are involved in a citation but are already
    present inside Wikidata and were successfully reconciled)! They aren't currently included
    in the output file of this function: this means that the associated citations will not be
    created by the `run_process_citations.py` script...

    :param second_batch: A batch of WDEntities which are supposedly involved in a citation
    """
    with open(pusher_citations_csv_file, 'a', encoding='utf-8') as f:
        for key, value in second_batch.items():
            if WDEntity.is_not_null(value.qid):
                line: str = str(key) + ',' + value.qid + '\n'
                f.write(line)


def process_chunk(chunk_filepath: str):
    """
    This function handles all the steps which are needed to fully process a single
    chunk of the input dataset.
      - Firstly, the RDF graph serialized inside the chunk file
        is imported in the form of an oc_ocdm's GraphSet.
      - Secondly, a loop over each BR entity
        is performed: the OCDM entities are parsed, reconciled with Wikidata and then converted
        into two batches of WDEntity instances.
      - Lastly, the two batches are uploaded to Wikidata
        and the citations CSV file is exported in order to support the run_process_citations.py script,
        which should be executed afterwards.

    :param chunk_filepath: A string representing the filesystem path to the chunk to be imported
    """
    # PROCESS INITIALIZATION
    rec: Reconciliator = Reconciliator()
    upload_batches: List[Dict[URIRef, WDEntity]] = [{}, {}]
    wikipedia_batch: Dict[URIRef, EnWikiPageWDEntity] = {}

    # DATA IMPORT PHASE
    graph_chunk: Graph = Graph().parse(location=chunk_filepath, format='nt11')

    g_set: GraphSet = GraphSet(base_iri, wanted_label=False)
    Reader.import_entities_from_graph(g_set, graph_chunk, resp_agent, enable_validation=False)

    # DATA PROCESSING PHASE
    for cur_br in g_set.get_br():
        if is_wikipedia_page(cur_br):
            process_wikipedia_page(cur_br, wikipedia_batch, rec)
        else:
            process_bibliographic_resource(cur_br, upload_batches, rec)

    # DATA UPLOAD PHASE
    first_batch: Dict[URIRef, WDEntity] = upload_batches[0]
    second_batch: Dict[URIRef, WDEntity] = upload_batches[1]

    if len(first_batch) > 0:
        upload_batch(first_batch)
        rec.reconciliate_batch(first_batch)

    if len(wikipedia_batch) > 0:
        upload_batch(wikipedia_batch)
        rec.reconciliate_wikipedia_batch(wikipedia_batch)

    if len(second_batch) > 0:
        upload_batch(second_batch)
        rec.reconciliate_batch(second_batch)
        store_citations_csv_file(second_batch)


"""
Entry point of the run_process.py script.
This process is supposed to reconcile and upload the entities contained in
the output files of the Enricher scripts. Along with their reconciliation,
entities are converted into the Wikidata's data-model and finally bulk-uploaded
through the use of QuickStatements.
"""
if __name__ == "__main__":
    # Removing trailing file separators:
    while base_dir[-1] == os.sep:
        base_dir = base_dir[:-1]

    files: List[str] = glob.glob(base_dir + os.sep + "*.nt", recursive=False)
    if len(files) <= 0:
        print("No file to be processed. Terminating the process...")
    else:
        print(f"{len(files)} files to be processed. Please wait...")
        print("START")

        # Each input files must be processed sequentially:
        for file in files:
            print("!" * 80)
            print(f"Processing: {file}")
            print("!" * 80)
            process_chunk(file)

        print("END")
