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

import os
from conf import rdf_input_dir, base_iri, resp_agent, rdf_output_dir, info_dir, supplier_prefix

from oc_ocdm import Reader
from oc_ocdm.graph import GraphSet
from rdflib import Graph
from oc_graphenricher.enricher import GraphEnricher
from oc_graphenricher.instancematching import InstanceMatching


def process_chunk(filename: str) -> None:
    """
    This function wraps the functionality of the external library 'oc_graphenricher'.
    It imports an OCDM compliant RDF chunk file, it tries to enrich it with external identifiers
    and then deduplicates its entities.

    :param filename: a string representing the filename (without the path) of the chunk file to be processed
    """
    filepath: str = os.path.join(rdf_input_dir, filename)
    filename_without_extension: str = os.path.splitext(filename)[0]

    g: Graph = Graph()
    g = g.parse(filepath, format='nt11')

    reader: Reader = Reader()
    g_set: GraphSet = GraphSet(base_iri=base_iri,
                               info_dir=info_dir,
                               supplier_prefix=supplier_prefix,
                               wanted_label=False)
    reader.import_entities_from_graph(g_set, g, enable_validation=False, resp_agent=resp_agent)

    # Enrichment
    enriched_filepath: str = rdf_output_dir + os.sep + 'enriched' + os.sep +\
        filename_without_extension + '.nt'
    enriched_prov: str = rdf_output_dir + os.sep + 'enriched' + os.sep + 'prov' + os.sep +\
        filename_without_extension + '.nq'
    # Output folders are created if not already existing
    if not os.path.exists(os.path.dirname(enriched_filepath)):
        os.makedirs(os.path.dirname(enriched_filepath))
    if not os.path.exists(os.path.dirname(enriched_prov)):
        os.makedirs(os.path.dirname(enriched_prov))

    enricher: GraphEnricher = GraphEnricher(g_set,
                                            graph_filename=enriched_filepath,
                                            provenance_filename=enriched_prov,
                                            info_dir=info_dir,
                                            debug=False,
                                            serialize_in_the_middle=False)
    enricher.enrich()

    # Deduplication
    deduplicated_filepath: str = rdf_output_dir + os.sep + 'deduplicated' + os.sep +\
        filename_without_extension + '.nt'
    deduplicated_prov: str = rdf_output_dir + os.sep + 'deduplicated' + os.sep + 'prov' + os.sep + \
        filename_without_extension + '.nq'
    # Output folders are created if not already existing
    if not os.path.exists(os.path.dirname(deduplicated_filepath)):
        os.makedirs(os.path.dirname(deduplicated_filepath))
    if not os.path.exists(os.path.dirname(deduplicated_prov)):
        os.makedirs(os.path.dirname(deduplicated_prov))

    matcher = InstanceMatching(g_set,
                               graph_filename=deduplicated_filepath,
                               provenance_filename=deduplicated_prov,
                               info_dir=info_dir,
                               debug=False)
    matcher.match()


""" Entry point of the run_process.py script.
This process is supposed to enrich and deduplicate the RDF files produced by the Converter step,
storing the new RDF files in a separate folder.
"""
if __name__ == '__main__':
    # Removing trailing file separators:
    while rdf_input_dir[-1] == os.sep:
        rdf_input_dir = rdf_input_dir[:-1]
    while rdf_output_dir[-1] == os.sep:
        rdf_output_dir = rdf_output_dir[:-1]

    print("START")
    # The chunk files must be processed sequentially, since oc_ocdm is still thread unsafe!
    for chunk_file in os.listdir(rdf_input_dir):
        if chunk_file.endswith('.nt'):
            print(f"Processing {chunk_file}...")
            process_chunk(chunk_file)
    print("END")
