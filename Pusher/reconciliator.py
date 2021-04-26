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

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Optional, List
    from rdflib import URIRef
    from entities.EnWikiPageWDEntity import EnWikiPageWDEntity

from rdflib import Namespace
from config import query_timeout, query_wait_time
from id_utils.isbn_utils import isbn_length
from entities.WDEntity import WDEntity
from SPARQLWrapper import SPARQLWrapper, XML


class Reconciliator(object):
    """
    The class held responsible for the reconciliation process of OCDM entities.
    """

    datacite = Namespace('http://purl.org/spar/datacite/')

    wd_isbn13 = 'P212'
    wd_isbn10 = 'P957'

    ocdm_to_wikidata = {
        datacite.orcid: 'P496',
        datacite.doi: 'P356',
        datacite.pmid: 'P698',
        datacite.pmcid: 'P932',
        datacite.issn: 'P236',
        datacite.wikipedia: None,  # TODO: a new property should be created for Wikipedia IDs
        datacite.viaf: 'P214'
    }

    def __init__(self):
        self._matches: Dict[URIRef, str] = {}

    def _from_ocdm_to_wikidata(self, uri: URIRef):
        if uri in self.ocdm_to_wikidata:
            return self.ocdm_to_wikidata[uri]
        else:
            return None

    def _add_match(self, res: URIRef, qid: str):
        self._matches[res] = qid

    def get_match(self, res: URIRef) -> Optional[str]:
        """
        Returns the required match against a given OCDM IRI.
        If absent, it returns None, otherwise the corresponding
        Wikidata ID in the form 'Qxxx'.

        :param res: The OCDM IRI of the entity of which the Wikidata ID must be returned
        :return: The required match, if existing
        """
        if res in self._matches:
            return self._matches[res]
        else:
            return None

    def reconciliate(self, res: URIRef, id_dict: dict):
        """
        Reconciliation of a generic OCDM entity. Reconciliation is done based on the list of
        IDs associated to the OCDM entity. If the reconciliation is successful, the retrieved
        Wikidata ID is internally stored in the self._matches dictionary.

        :param res: The OCDM IRI of the generic entity to be reconciled
        :param id_dict: A dictionary containing the IDs associated with the generic entity to be reconciled
        """
        existing_match: Optional[str] = self.get_match(res)
        if existing_match is not None:
            # This entity already has a match, running again the query is pointless!
            return

        # We need at least one ID for the reconciliation
        if len(id_dict) > 0:
            if 'wikidata' in id_dict and id_dict['wikidata'] is not None:
                # We already have the wikidata ID, we don't need reconciliation!
                self._add_match(res, id_dict['wikidata'])
                return

            query: str = f'SELECT ?item WHERE {{ VALUES (?id_prop ?id_value) {{ '
            for id_scheme, id_value in id_dict.items():
                if id_scheme == self.datacite.isbn:
                    # ISBNs are handled differently...
                    isbn_len: int = isbn_length(id_value)
                    if isbn_len == 13:
                        id_prop: Optional[str] = self.wd_isbn13
                    elif isbn_len == 10:
                        id_prop: Optional[str] = self.wd_isbn10
                    else:
                        # This SHOULD never happen (at least in theory)...
                        id_prop: Optional[str] = None
                else:
                    id_prop: Optional[str] = self._from_ocdm_to_wikidata(id_scheme)

                if id_prop is not None:
                    query += f'(wdt:{id_prop} \"{id_value}\") '

            query += f'}} ?item ?id_prop ?id_value. }} LIMIT 1'
            results: List[Dict[str, Dict[str, str]]] = self._query_wikidata(query)
            if len(results) > 0:
                qid: str = results[0]['item']['value']
                qid = qid[31:]  # remove the "http://www.wikidata.org/entity/" part
                self._add_match(res, qid)

    def reconciliate_wikipedia_page(self, res: URIRef, title: str):
        """
        Reconciliation of a Wikipedia page. Since our workflow is currently limited to enwiki pages,
        reconciliation is done based on the match between the english label of the Wikidata entity
        and the page title. If the reconciliation is successful, the retrieved Wikidata ID is internally
        stored in the self._matches dictionary.

        PLEASE NOTE: the query could be improved by checking also the match with the Wikipedia ID of
        the given page. This wasn't done because of the lack of a Wikidata property for 'has Wikipedia ID'.

        :param res: The OCDM IRI of the BR entity to be reconciled
        :param title: The enwiki page title of the Wikipedia page to be reconciled
        """
        existing_match: Optional[str] = self.get_match(res)
        if existing_match is not None:
            # This entity already has a match, running again the query is pointless!
            return

        if title is not None:
            query: str = f'SELECT ?item WHERE {{ ' \
                         f'?item wdt:P31 wd:Q50081413; rdfs:label \"{title}\"@en. }} LIMIT 1'
            results: List[Dict[str, Dict[str, str]]] = self._query_wikidata(query)
            if len(results) > 0:
                qid: str = results[0]['item']['value']
                qid = qid[31:]  # remove the "http://www.wikidata.org/entity/" part
                self._add_match(res, qid)

    @staticmethod
    def _query_wikidata(query: str) -> List[Dict[str, Dict[str, str]]]:
        """
        Static helper function which performs a SPARQL query to the Wikidata endpoint.

        :param query: A string containing the SPARQL query to be executed
        :return: The list of result bindings
        """
        sparql = SPARQLWrapper('https://query.wikidata.org/sparql',
                               agent="Pusher (via OpenCitations - http://opencitations.net;"
                                     " mailto:contact@opencitations.net)")
        sparql.setTimeout(query_timeout)
        sparql.setReturnFormat(XML)
        sparql.setQuery(query)
        time.sleep(query_wait_time)  # Wikidata limits the max. number of queries per minute! We have to wait...
        return sparql.queryAndConvert().bindings

    def reconciliate_batch(self, batch: Dict[URIRef, WDEntity]):
        """
        Wrapper function that calls 'reconciliate' over each WDEntity
        contained in the given batch.

        :param batch: A dictionary representing the batch of WDEntity instances to be reconciled
        """
        for res, entity in batch.items():
            if not WDEntity.is_not_null(entity.qid):
                id_dict: Dict[str, str] = entity.id_dict
                self.reconciliate(res, id_dict)
                match: Optional[str] = self.get_match(res)

                if match is not None:
                    entity.qid = match

    def reconciliate_wikipedia_batch(self, batch: Dict[URIRef, EnWikiPageWDEntity]):
        """
        Wrapper function that calls 'reconciliate_wikipedia_page' over each EnWikiPageWDEntity
        contained in the given batch.

        :param batch: A dictionary representing the batch of EnWikiPageWDEntity instances to be reconciled
        """
        for res, entity in batch.items():
            if not WDEntity.is_not_null(entity.qid):
                title: Optional[str] = entity.data['title']
                if title is not None:
                    self.reconciliate_wikipedia_page(res, title)
                    match: Optional[str] = self.get_match(res)

                    if match is not None:
                        entity.qid = match
