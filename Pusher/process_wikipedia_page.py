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
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic import BibliographicResource
    from reconciliator import Reconciliator

from entities.EnWikiPageWDEntity import EnWikiPageWDEntity
from id_extractor import extract_wikipedia_id


def process_wikipedia_page(br: BibliographicResource, wikipedia_batch: Dict[URIRef, EnWikiPageWDEntity],
                           rec: Reconciliator):
    """
    This function handles the processing of a Wikipedia page. It tries to reconcile it
    and then it creates an appropriate EnWikiPageWDEntity instance which is stored inside
    the given batch. Because of how the previous steps of the workflow work, here it can
    be safely assumed that each BR entity representing a Wikipedia page has a proper title
    and Wikipedia ID with which reconciliation could be done.

    :param br: The BR entity to be processed
    :param wikipedia_batch: The dictionary in which new EnWikiPageWDEntity instances will be stored
    :param rec: A Reconciliator instance
    """

    if br.res not in wikipedia_batch:
        # Here we collect data needed for reconciliation:
        title = br.get_title()

        # Reconciliation:
        rec.reconciliate_wikipedia_page(br.res, title)
        match = rec.get_match(br.res)

        if match is not None:
            # Successful reconciliation
            wikipedia_batch[br.res] = EnWikiPageWDEntity(qid=match)
        else:
            # Failed reconciliation
            entity = EnWikiPageWDEntity()

            # Identifiers extraction:
            entity.id_dict['wikipedia'] = extract_wikipedia_id(br)

            # Sitelink extraction:
            entity.sitelink = br.get_title()

            # The end of the process:
            wikipedia_batch[br.res] = entity
