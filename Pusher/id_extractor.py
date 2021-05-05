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
    from typing import Dict, Optional, List
    from rdflib import URIRef
    from oc_ocdm.graph.entities import BibliographicEntity, Identifier
    from oc_ocdm.graph.entities.bibliographic import BibliographicResource

from oc_ocdm.graph import GraphEntity
from rdflib import Namespace
from id_utils.isbn_utils import isbn10_is_valid, isbn_length, isbn_normalize, isbn13_is_valid, from_isbn10_to_isbn13, \
    from_isbn13_to_isbn10
from id_utils.issn_utils import normalize_issn, issn_is_valid
from id_utils.orcid_utils import normalize_orcid, orcid_is_valid


def extract_ids(element: BibliographicEntity) -> Dict[str, str]:
    """
    Extracts all the IDs associated with the given BR entity into a dictionary.

    :param element: The generic entity from which to extract the ID dictionary
    :return: The ID dictionary associated extracted from the given generic entity
    """
    result_dict = {}
    id_list = element.get_identifiers()
    for identifier in id_list:
        scheme = identifier.get_scheme()
        value = identifier.get_literal_value()
        if scheme == GraphEntity.iri_orcid:
            # ORCID can be handled in a "smarter" way:
            normalized_orcid = normalize_orcid(value)
            if orcid_is_valid(normalized_orcid):
                # It gets normalized into a xxxx-xxxx-xxxx-xxx[check digit] format:
                result_dict['orcid'] = normalized_orcid
            else:
                print("Invalid ORCID found (wrong length, format or check digit): " + value)
        elif scheme == GraphEntity.iri_doi:
            result_dict['doi'] = value.upper()  # Wikidata stores DOIs as uppercase strings
        elif scheme == GraphEntity.iri_pmid:
            result_dict['pmid'] = value  # just a number
        elif scheme == GraphEntity.iri_pmcid:
            result_dict['pmcid'] = value  # just a number
        elif scheme == GraphEntity.iri_issn:
            # ISSN can be handled in a "smarter" way:
            normalized_issn = normalize_issn(value)
            if issn_is_valid(normalized_issn):
                # It gets normalized into a xxxx-xxx[check digit] format:
                result_dict['issn'] = normalized_issn
            else:
                print("Invalid ISSN found (wrong length, format or check digit): " + value)
        elif scheme == GraphEntity.iri_isbn:
            # ISBN can be handled in a "smarter" way:
            normalized_isbn = isbn_normalize(value)
            isbn_len = isbn_length(normalized_isbn)
            if isbn_len == 10:
                if isbn10_is_valid(normalized_isbn):
                    # It gets normalized into a number (containing '-' chars) + check:
                    result_dict['isbn10'] = normalized_isbn
                else:
                    print("Invalid ISBN10 found (wrong check digit): " + value)
            elif isbn_len == 13:
                if isbn13_is_valid(normalized_isbn):
                    # It gets normalized into a number (containing '-' chars) + check:
                    result_dict['isbn13'] = normalized_isbn
                else:
                    print("Invalid ISBN13 found (wrong check digit): " + value)
            else:
                print("Invalid ISBN found (wrong length): " + value)
        elif scheme == GraphEntity.iri_wikidata:
            result_dict['wikidata'] = value  # if we had this, we would not need reconciliation
        elif scheme == GraphEntity.iri_wikipedia:
            result_dict['wikipedia'] = value  # just a number
        elif scheme == GraphEntity.iri_viaf:
            result_dict['viaf'] = value  # just a number

    # Automatically infer missing ISBNs:
    if ('isbn10' in result_dict and result_dict['isbn10'] is not None) and \
            ('isbn13' not in result_dict or result_dict['isbn13'] is None):
        result_dict['isbn13'] = from_isbn10_to_isbn13(result_dict['isbn10'])
    elif ('isbn13' in result_dict and result_dict['isbn13'] is not None) and \
            ('isbn10' not in result_dict or result_dict['isbn10'] is None):
        result_dict['isbn10'] = from_isbn13_to_isbn10(result_dict['isbn13'])
    return result_dict


def extract_wikipedia_id(br: BibliographicResource) -> Optional[str]:
    """
    Extracts the firstly-found Wikipedia ID literal value associated with the given BR entity.

    :param br: The BR entity from which to extract the Wikipedia ID
    :return: The Wikipedia ID literal value associated with the given BR entity, if present
    """
    datacite: Namespace = Namespace('http://purl.org/spar/datacite/')
    wikipedia_id: Optional[str] = None

    id_list: List[Identifier] = br.get_identifiers()
    for identifier in id_list:
        id_scheme: Optional[URIRef] = identifier.get_scheme()
        id_value: Optional[str] = identifier.get_literal_value()
        if id_scheme == datacite.wikipedia:
            wikipedia_id = id_value
            break
    return wikipedia_id


def id_dict_is_empty(id_dict: Dict[str, str]) -> bool:
    """
    This predicate can be used to know if the ID dictionary extracted from an OCDM entity
    is effectively empty.

    :param id_dict: The ID dictionary to be checked
    :return: True if the ID dictionary is empty, False otherwise
    """
    if len(id_dict) <= 0:
        return True
    else:
        for key, value in id_dict.items():
            if key is not None and key != '' and value is not None and value != '':
                return False
        return True
