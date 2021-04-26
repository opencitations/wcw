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
    from typing import Dict
    from oc_ocdm.graph.entities.bibliographic import BibliographicResource, Citation
    from oc_ocdm.graph.entities import Identifier

import os
import time
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

from conf.conf_citations import *

# Utils
from utils.id_list_utils import parse_id_list_repeated_schemes

# oc_ocdm
from oc_ocdm.graph import GraphSet
from oc_ocdm.prov import ProvSet
from oc_ocdm import Storer
from rdflib import URIRef


def update_tmp_to_meta(cur_csv_file: str, tmp_to_meta: Dict[str, str]) -> Dict[str, str]:
    """
    This function is able to parse a CSV file which was produced by 'meta' and to extract from it
    the mappings between 'tmp' identifiers (which were uniquely assigned to each resource by the
    run_process.py script) and the corresponding 'meta' identifiers (associated to a resource --or to
    a set of deduplicated resources-- by the 'meta' script.

    This is why the ordering of Converter scripts execution must be:

    * 1st --> run_process.py
    * 2nd --> meta
    * 3rd --> run_process_citations.py

    :param cur_csv_file: The filename (without the path) of the CSV file from which to extract mappings
    :param tmp_to_meta: The mapping dictionary to be updated
    :return: The dictionary given as input, enriched with new mapping extracted from the given CSV file
    """
    filepath = os.path.join(meta_csv_output_dir, cur_csv_file)
    df = pd.read_csv(filepath, usecols=['id'], low_memory=False)
    df['id'] = df['id'].astype(str).map(parse_id_list_repeated_schemes)
    id_col = df['id'].to_numpy(copy=False)

    update_dict = {}
    for row in id_col:
        if 'tmp' in row and 'meta':
            meta_id = row['meta'][0]
            for cur_tmp in row['tmp']:
                update_dict[cur_tmp] = meta_id

    tmp_to_meta.update(update_dict)
    return tmp_to_meta


def tmp_to_meta_mapping(series: pd.Series, conversion_dict: Dict[str, str]) -> None:
    """
    This function applies the 'tmp-to-meta' mapping to a Pandas Series of 'tmp' identifiers.
    Whether a 'meta' identifier could not be found for a particular 'tmp' value, that same
    'tmp' string is replaced by a None value and the corresponding citation won't be produced
    in the output RDF file.

    :param series: A Pandas Series containing 'tmp' identifiers to be mapped onto their respective 'meta' identifiers
    :param conversion_dict: The dictionary that maps 'tmp' identifiers onto their respective 'meta' identifiers
    """
    # Here the Pandas Series is converted into a Numpy array
    # so that we can iterate way faster over its elements:
    series_col = series.to_numpy(copy=False)
    for i, row in enumerate(series_col):
        if row is not None and row in conversion_dict and conversion_dict[row] is not None:
            series_col[i] = conversion_dict[row]
        else:
            series_col[i] = None


def process(cur_citations_file: str, conversion_dict: Dict[str, str]) -> None:
    """
    This function takes care of generating an OCDM compliant RDF file containing
    the Citation entities that describe the relations between citing Wikipedia pages
    and cited bibliographic resources.

    Additionally, a CSV file compliant with other OpenCitations tools is produced. Since this
    is not strictly needed for the 'Wikipedia Citations in Wikidata' workflow, those files
    can be safely ignored.

    Please note: the bool flag 'rdf_output_in_chunks' from conf/conf_citations.py MUST be set to True,
    otherwise the following scripts of the workflow (Enricher and Pusher) won't be able to import
    the intermediate RDF files produced by this script.

    :param cur_citations_file: The filename (without the path) of the CSV file to be converted
    :param conversion_dict: The dictionary that maps 'tmp' identifiers onto their respective 'meta' identifiers
    """
    filepath: str = os.path.join(citations_csv_dir, cur_citations_file)
    df: pd.DataFrame = pd.read_csv(filepath, usecols=['citing', 'cited'], low_memory=False)

    # 'tmp-to-meta' mapping is applied to each column of the DataFrame
    tmp_to_meta_mapping(df['citing'], conversion_dict)
    tmp_to_meta_mapping(df['cited'], conversion_dict)

    # Rows containing None values are dropped: we cannot generate valid Citation entities for them
    df = df.dropna(axis=0, how='any', subset=['citing', 'cited'])
    df = df.reset_index(drop=True)

    # The DataFrame is enriched with additional columns that are needed for achieving full
    # compliance with other OpenCitations tools. This is not strictly needed for our workflow:
    df['id'] = None
    df['oci'] = None
    df['creation'] = None  # not applicable (the citation comes from a Wikipedia page)
    df['timespan'] = None  # not applicable (the citation comes from a Wikipedia page)
    df['journal_sc'] = 'no'
    df['author_sc'] = 'no'

    # A temporary GraphSet is used to instantiate BibliographicResource entities that are needed
    # for the creation of Citation entities but that won't be kept in the output RDF file:
    temp_gs: GraphSet = GraphSet(base_iri)

    # The actual GraphSet that will contain the Citation entities to be stored in the output RDF file:
    ci_gs: GraphSet = GraphSet(base_iri, info_dir=converter_citations_info_dir, supplier_prefix=supplier_prefix,
                               wanted_label=False)

    # Here the DataFrame columns are converted into Numpy arrays
    # so that we can iterate way faster over their elements:
    citing_col = df['citing'].to_numpy(copy=False)
    cited_col = df['cited'].to_numpy(copy=False)
    id_col = df['id'].to_numpy(copy=False)
    oci_col = df['oci'].to_numpy(copy=False)

    for i, (citing_meta_id, cited_meta_id) in enumerate(zip(citing_col, cited_col)):
        citing_res: URIRef = URIRef(base_iri + citing_meta_id)
        cited_res: URIRef = URIRef(base_iri + cited_meta_id)

        # A query is performed to discover if the current citation has already been processed:
        query_string: str = f'''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX cito: <http://purl.org/spar/cito/>
        PREFIX datacite: <http://purl.org/spar/datacite/>
        PREFIX literal: <http://www.essepuntato.it/2010/06/literalreification/>

        SELECT ?ci_res ?oci
        FROM <https://w3id.org/oc/meta/ci/>
        WHERE {{
            ?ci_res rdf:type cito:Citation ;
                    cito:hasCitingEntity <{citing_res}> ;
                    cito:hasCitedEntity <{cited_res}> .
            OPTIONAL {{
                ?ci_res datacite:hasIdentifier ?id .
                ?id	datacite:usesIdentifierScheme datacite:oci ;
                    literal:hasLiteralValue ?oci .
            }}
        }}
        LIMIT 1
        '''
        tp: SPARQLWrapper = SPARQLWrapper(triplestore_url)
        tp.setTimeout(query_timeout)
        tp.setMethod('GET')
        tp.setQuery(query_string)
        tp.setReturnFormat(JSON)
        results = tp.queryAndConvert()
        bindings = results["results"]["bindings"]

        if len(bindings) >= 1:  # 'LIMIT 1' in the query string should guarantee a maximum of 1 returned binding
            # This citation is already stored in the triplestore!
            row: Dict = bindings[0]

            # Update the output dataframe
            ci_res: URIRef = URIRef(bindings[0]["ci_res"]["value"])
            id_col[i] = str(ci_res)[len(base_iri):]

            if "oci" in row:
                oci_col[i] = row["oci"]["value"]
        else:
            # This citation is currently missing from the triplestore!

            # Create BR entities in "append mode" by providing 'res' without 'preexisting_graph'
            citing_br: BibliographicResource = temp_gs.add_br(resp_agent, res=citing_res, preexisting_graph=None)
            cited_br: BibliographicResource = temp_gs.add_br(resp_agent, res=cited_res, preexisting_graph=None)

            # Create OCI identifier
            oci_str: str = str(citing_res)[len(base_iri + 'br/'):] + '-' + str(cited_res)[len(base_iri + 'br/'):]
            oci: Identifier = ci_gs.add_id(resp_agent)
            oci.create_oci(oci_str)

            # Create citation
            ci: Citation = ci_gs.add_ci(resp_agent)
            ci.has_identifier(oci)
            ci.has_citing_entity(citing_br)
            ci.has_cited_entity(cited_br)

            # Update the output dataframe
            id_col[i] = str(ci.res)[len(base_iri):]
            oci_col[i] = oci_str

    # Store the dataframe as a CSV file that's compliant with OpenCitations tools:
    output_filepath: str = os.path.join(converter_citations_csv_output_dir, cur_citations_file)
    df.to_csv(output_filepath, index=False, chunksize=100000,
              columns=['id', 'oci', 'citing', 'cited', 'creation',
                       'timespan', 'journal_sc', 'author_sc'])

    # Store new citations in an RDF file (together with the related provenance).
    # They should also be uploaded to the triplestore so to update the current state
    # of execution: by this way, they won't be created again since they will already
    # be present inside the triplestore.
    ci_ps: ProvSet = ProvSet(ci_gs, base_iri)
    ci_ps.generate_provenance()

    ci_storer: Storer = Storer(ci_gs,
                               dir_split=dir_split_number,
                               n_file_item=items_per_file,
                               default_dir=default_dir,
                               output_format='nt11')
    ci_prov_storer: Storer = Storer(ci_ps,
                                    dir_split=dir_split_number,
                                    n_file_item=items_per_file,
                                    default_dir=default_dir,
                                    output_format='nquads')

    if rdf_output_in_chunks:
        # The RDF files are stored WITHOUT following the folder structure
        # adopted by OpenCitations: all the newly created citations are kept
        # in a single file.
        # In the following steps of the workflow, every script assumes that data was produced in chunks:
        # this means that this modality should never be chosen and that 'rdf_output_in_chunks' must
        # be set to True.
        filename_without_csv: str = cur_citations_file[:-4]

        # Data
        f: str = os.path.join(converter_citations_rdf_output_dir, filename_without_csv + ".ttl")
        ci_storer.store_graphs_in_file(f, context_path)
        ci_storer.upload_all(triplestore_url, converter_citations_rdf_output_dir, batch_size=100)

        # Provenance
        prov_dir: str = os.path.join(converter_citations_rdf_output_dir, 'prov')
        if not os.path.exists(os.path.dirname(prov_dir)):
            os.makedirs(os.path.dirname(prov_dir))
        f_prov: str = os.path.join(prov_dir, filename_without_csv + '.nquads')
        ci_prov_storer.store_graphs_in_file(f_prov, context_path)
    else:
        # The RDF files are stored following the folder structure adopted by OpenCitations.
        # Newly created citations could be split into different files based on
        # various conditions.
        # In the following steps of the workflow, every script assumes that data was produced in chunks:
        # this means that this modality should never be chosen and that 'rdf_output_in_chunks' must
        # be set to True.
        ci_storer.upload_and_store(
            converter_citations_rdf_output_dir, triplestore_url, base_iri, context_path, batch_size=100)

        ci_prov_storer.store_all(
            converter_citations_rdf_output_dir, base_iri, context_path)


""" Entry point of the run_process_citations.py script.
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

    # Fix config value
    if base_iri[-1] != '/':
        base_iri += '/'
    if not os.path.exists(converter_citations_csv_output_dir):
        os.mkdir(converter_citations_csv_output_dir)

    # The mapping dictionary is built here (from 'tmp:XXX' to 'meta:YYY' identifier):
    tmp_to_meta_dict = {}
    for csv_file in os.listdir(meta_csv_output_dir):
        if csv_file.endswith('.csv'):
            tmp_to_meta_dict = update_tmp_to_meta(csv_file, tmp_to_meta_dict)

    # The mapping dictionary is used to convert the citations CSV files.
    # Please note: since we need to avoid duplicates amongst Citation entities
    # and we achieve this by querying a triplestore that at each moment will contain
    # the state of this script's execution, then we are forced to proceed
    # sequentially with a simple for loop:
    for citation_file in os.listdir(citations_csv_dir):
        if citation_file.endswith('.csv'):
            process(citation_file, tmp_to_meta_dict)

    end = time.time()
    print("END %d seconds elapsed." % (end - start))
