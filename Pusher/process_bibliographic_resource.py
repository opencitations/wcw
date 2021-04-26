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
    from typing import Optional, List, Dict
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic import BibliographicResource, ResponsibleAgent
    from entities.WDEntity import WDEntity

from rdflib import Namespace
from id_extractor import extract_ids, id_dict_is_empty
from reconciliator import Reconciliator

from oc_ocdm.support.support import get_ordered_contributors_from_br

from entities.BibliographicWDEntity import BibliographicWDEntity
from entities.HumanWDEntity import HumanWDEntity
from entities.OrganizationWDEntity import OrganizationWDEntity

fabio = Namespace("http://purl.org/spar/fabio/")
doco = Namespace("http://purl.org/spar/doco/")


def _is_journal_article(br: BibliographicResource) -> bool:
    types = br.get_types()
    return fabio.JournalArticle in types


def _is_proceedings_article(br: BibliographicResource) -> bool:
    types = br.get_types()
    return fabio.ProceedingsPaper in types


def _is_book(br: BibliographicResource) -> bool:
    types = br.get_types()
    return fabio.Book in types


def _is_book_part(br: BibliographicResource) -> bool:
    types = br.get_types()
    condition_a = doco.Part in types

    book = br.get_is_part_of()
    condition_b = book is not None

    if book is not None:
        condition_c = _is_book(book)
    else:
        condition_c = False

    return condition_a and condition_b and condition_c


def _is_book_chapter(br: BibliographicResource) -> bool:
    types = br.get_types()
    return fabio.BookChapter in types


def _is_journal(br: BibliographicResource) -> bool:
    types = br.get_types()
    return fabio.Journal in types


def get_instance_of_br(br: BibliographicResource) -> Optional[str]:
    """
    This function infers the Wikidata category related to the given BR entity.
    Should the type of BR entity be unknown, None will be returned.

    PLEASE NOTE: the Wikidata categories returned by this function should be
    reviewed and, if needed, changed.

    :param br: The BR entity
    :return: A string containing the Wikidata ID of the BR entity's category, if known
    """
    if _is_journal_article(br):
        return 'Q13442814'  # 'scholarly article'
    elif _is_proceedings_article(br):
        return 'Q23927052'  # 'conference paper'
    elif _is_book(br):
        return 'Q47461344'  # 'written work'
    elif _is_book_part(br):
        return 'Q47461344'  # 'written work'
    elif _is_book_chapter(br):
        return 'Q1980247'  # 'chapter (book chapter)'
    elif _is_journal(br):
        return 'Q737498'  # 'academic journal'
    else:
        # This line of code should be unreachable (at least, in theory)
        return None


def _get_unordered_ra_list(br: BibliographicResource, role_type: URIRef) -> List[ResponsibleAgent]:
    # Helper function used inside 'process_bibliographic_resource':
    result_list: List[ResponsibleAgent] = []
    for contributor in br.get_contributors():
        role_type = contributor.get_role_type()
        resp_agent = contributor.get_is_held_by()
        if role_type is not None and role_type == role_type and resp_agent is not None:
            result_list.append(resp_agent)
    return result_list


def process_bibliographic_resource(br: BibliographicResource, upload_batches: List[Dict[URIRef, WDEntity]],
                                   rec: Reconciliator):
    """
    This function handles the processing of a BR entity. It tries to reconcile it
    and then it creates an appropriate BibliographicWDEntity instance which is stored inside
    the proper batch. Because of how the previous steps of the workflow work, here we cannot
    know a-priori if the entity represents a proper bibliographic resource or a venue which
    contains other BR entities: in the first case, the BibliographicWDEntity should be placed
    inside the second batch, while in the second case it should be placed inside the first batch.
    Entities without at least an ID will not be processed, since the Pusher relies on the presence
    of the IDs for the reconciliation step.

    :param br: The BR entity to be processed
    :param upload_batches: A list containing the two dictionaries in which new WDEntity instances will be stored
    :param rec: A Reconciliator instance
    """
    first_batch = upload_batches[0]
    second_batch = upload_batches[1]

    if br.res in first_batch and br.res in second_batch:
        # This condition means somewhere a big mistake was made.
        # This should never happen. If it happens, we may try
        # to fix the problem in the most sensible way:
        del second_batch[br.res]
    elif br.res not in first_batch and br.res not in second_batch:
        # Here we collect data needed for reconciliation:
        id_dict = extract_ids(br)  # extract and normalize IDs
        if id_dict_is_empty(id_dict):
            # No identifiers that could be used in the later reconciliation
            # process. We won't create this entity...
            return

        # Reconciliation:
        rec.reconciliate(br.res, id_dict)
        match = rec.get_match(br.res)

        if match is not None:
            # Successful reconciliation
            second_batch[br.res] = BibliographicWDEntity(qid=match, instance_of=get_instance_of_br(br))
        else:
            entity = BibliographicWDEntity(instance_of=get_instance_of_br(br))

            # Identifiers extraction:
            entity.id_dict.update(id_dict)

            # Title extraction [P1476]:
            entity.data['title'] = br.get_title()

            # Publication date extraction [P577]:
            entity.data['publication_date'] = br.get_pub_date()

            # Venue extraction [P1433]:
            venue = br.get_is_part_of()
            if venue is not None:
                process_venue(venue, entity, upload_batches, rec)

            pro = Namespace("http://purl.org/spar/pro/")

            # Authors extraction [P50/P2093]:
            try:
                # 'get_ordered_contributors_from_br' is a function belonging to the oc_ocdm package!
                authors_list: List[ResponsibleAgent] = get_ordered_contributors_from_br(br, pro.author)
            except ValueError:
                authors_list: List[ResponsibleAgent] = _get_unordered_ra_list(br, pro.author)

            for idx, author in enumerate(authors_list):
                idx += 1  # Wikidata counts from 1 to N, not from 0 to N-1!
                process_author(author, idx, entity, upload_batches, rec)

            # Editor extraction [P98]:
            try:
                # 'get_ordered_contributors_from_br' is a function belonging to the oc_ocdm package!
                editors_list: List[ResponsibleAgent] = get_ordered_contributors_from_br(br, pro.editor)
            except ValueError:
                editors_list: List[ResponsibleAgent] = _get_unordered_ra_list(br, pro.editor)

            for idx, editor in enumerate(editors_list):
                idx += 1  # Wikidata counts from 1 to N, not from 0 to N-1!
                process_editor(editor, idx, entity, upload_batches, rec)

            # Publisher extraction [P123]:
            try:
                # 'get_ordered_contributors_from_br' is a function belonging to the oc_ocdm package!
                publishers_list: List[ResponsibleAgent] = get_ordered_contributors_from_br(br, pro.publisher)
            except ValueError:
                publishers_list: List[ResponsibleAgent] = _get_unordered_ra_list(br, pro.publisher)

            for idx, publisher in enumerate(publishers_list):
                idx += 1  # Wikidata counts from 1 to N, not from 0 to N-1!
                process_publisher(publisher, idx, entity, upload_batches, rec)

            # Page(s) extraction [P304]:
            re_list = br.get_formats()
            # Since this BR entity was generated by 'meta' during the Converter phase,
            # we can assume that there will only be one (optional) RE associated to it:
            if len(re_list) >= 1:
                re = re_list[0]
                start_page = re.get_starting_page()
                end_page = re.get_ending_page()

                if start_page is not None and end_page is not None:
                    entity.data['pages'] = start_page + '-' + end_page
                elif start_page is not None:
                    entity.data['pages'] = start_page
                elif end_page is not None:
                    entity.data['pages'] = end_page

            # The end of the process:
            second_batch[br.res] = entity


def process_venue(venue: BibliographicResource, br_entity: BibliographicWDEntity,
                  upload_batches: List[Dict[URIRef, WDEntity]], rec: Reconciliator):
    """
    This function handles the processing of a BR entity representing a venue that contains at least
    another BR entity. It tries to reconcile it and then it creates an appropriate BibliographicWDEntity
    instance which is stored inside the first batch. Entities without at least an ID will not be processed,
    since the Pusher relies on the presence of the IDs for the reconciliation step.

    :param venue: The BR entity (venue) to be processed
    :param br_entity: The BR entity whose venue is the 'venue' argument
    :param upload_batches: A list containing the two dictionaries in which new WDEntity instances will be stored
    :param rec: A Reconciliator instance
    """
    first_batch = upload_batches[0]
    second_batch = upload_batches[1]

    if venue.res in first_batch and venue.res in second_batch:
        # This condition means somewhere a big mistake was made.
        # This should never happen. If it happens, we may try
        # to fix the problem in the most sensible way:
        del second_batch[venue.res]
    elif venue.res in second_batch:
        # Since we now know that this entity is referenced as a venue
        # for another entity contained in the second_batch, we need
        # to move this entity into the first_batch:
        venue_entity = second_batch[venue.res]
        del second_batch[venue.res]
        first_batch[venue.res] = venue_entity
    elif venue.res not in first_batch and venue.res not in second_batch:
        # Here we collect data needed for reconciliation:
        id_dict = extract_ids(venue)  # extract and normalize IDs
        if id_dict_is_empty(id_dict):
            # No identifiers that could be used in the later reconciliation
            # process. We won't create this entity...
            return

        # Reconciliation:
        rec.reconciliate(venue.res, id_dict)
        match = rec.get_match(venue.res)

        if match is not None:
            # Successful reconciliation
            venue_entity = BibliographicWDEntity(qid=match, instance_of=get_instance_of_br(venue))
            first_batch[venue.res] = venue_entity
            br_entity.data['venue'] = venue_entity
        else:
            venue_entity = BibliographicWDEntity(instance_of=get_instance_of_br(venue))

            # Identifiers extraction:
            venue_entity.id_dict.update(id_dict)

            # Title extraction [P1476]:
            venue_entity.data['title'] = venue.get_title()

            # The end of the process:
            first_batch[venue.res] = venue_entity
            br_entity.data['venue'] = venue_entity


def process_author(ra: ResponsibleAgent, idx: int, br_entity: BibliographicWDEntity,
                   upload_batches: List[Dict[URIRef, WDEntity]], rec: Reconciliator):
    """
    This function handles the processing of an RA (author) entity. It tries to reconcile it
    and then it creates an appropriate HumanWDEntity instance which is stored inside
    the first batch. Entities without at least an ID will not be processed, since the Pusher
    relies on the presence of the IDs for the reconciliation step.

    :param ra: The RA (author) entity to be processed
    :param idx: An integer representing the order of the author inside the full list of authors
    :param br_entity: The BR entity whose author is the 'ra' argument
    :param upload_batches: A list containing the two dictionaries in which new WDEntity instances will be stored
    :param rec: A Reconciliator instance
    """
    first_batch = upload_batches[0]

    if ra.res not in first_batch:
        # Here we collect data needed for reconciliation:
        id_dict = extract_ids(ra)
        if id_dict_is_empty(id_dict):
            # No identifiers that could be used in the later reconciliation
            # process. We won't create this entity...
            return

        # Reconciliation:
        rec.reconciliate(ra.res, id_dict)
        match = rec.get_match(ra.res)

        if match is not None:
            # Successful reconciliation
            ra_entity = HumanWDEntity(qid=match)
            first_batch[ra.res] = ra_entity
            br_entity.authors[idx] = ra_entity
        else:
            # Failed reconciliation
            ra_entity = HumanWDEntity()

            # Identifiers extraction:
            ra_entity.id_dict.update(id_dict)

            # Given name extraction [P735]:
            ra_entity.data['given_name'] = ra.get_given_name()

            # Family name extraction [P734]:
            ra_entity.data['family_name'] = ra.get_family_name()

            # The end of the process:
            first_batch[ra.res] = ra_entity
            br_entity.authors[idx] = ra_entity


def process_editor(ra: ResponsibleAgent, idx: int, br_entity: BibliographicWDEntity,
                   upload_batches: List[Dict[URIRef, WDEntity]], rec: Reconciliator):
    """
    This function handles the processing of an RA (editor) entity. It tries to reconcile it
    and then it creates an appropriate HumanWDEntity instance which is stored inside
    the first batch. Entities without at least an ID will not be processed, since the Pusher
    relies on the presence of the IDs for the reconciliation step.

    :param ra: The RA (editor) entity to be processed
    :param idx: An integer representing the order of the editor inside the full list of editors
    :param br_entity: The BR entity whose editor is the 'ra' argument
    :param upload_batches: A list containing the two dictionaries in which new WDEntity instances will be stored
    :param rec: A Reconciliator instance
    """
    first_batch = upload_batches[0]

    if ra.res not in first_batch:
        # Here we collect data needed for reconciliation:
        id_dict = extract_ids(ra)
        if id_dict_is_empty(id_dict):
            # No identifiers that could be used in the later reconciliation
            # process. We won't create this entity...
            return

        # Reconciliation:
        rec.reconciliate(ra.res, id_dict)
        match = rec.get_match(ra.res)

        if match is not None:
            # Successful reconciliation
            ra_entity = HumanWDEntity(qid=match)
            first_batch[ra.res] = ra_entity
            br_entity.editors[idx] = ra_entity
        else:
            # Failed reconciliation
            ra_entity = HumanWDEntity()

            # Identifiers extraction:
            ra_entity.id_dict.update(id_dict)

            # Given name extraction [P735]:
            ra_entity.data['given_name'] = ra.get_given_name()

            # Family name extraction [P734]:
            ra_entity.data['family_name'] = ra.get_family_name()

            # The end of the process:
            first_batch[ra.res] = ra_entity
            br_entity.editors[idx] = ra_entity


def process_publisher(ra: ResponsibleAgent, idx: int, br_entity: BibliographicWDEntity,
                      upload_batches: List[Dict[URIRef, WDEntity]], rec: Reconciliator):
    """
    This function handles the processing of an RA (publisher) entity. It tries to reconcile it
    and then it creates an appropriate OrganizationWDEntity instance which is stored inside
    the first batch. Entities without at least an ID will not be processed, since the Pusher
    relies on the presence of the IDs for the reconciliation step.

    :param ra: The RA (publisher) entity to be processed
    :param idx: An integer representing the order of the publisher inside the full list of publishers
    :param br_entity: The BR entity whose publisher is the 'ra' argument
    :param upload_batches: A list containing the two dictionaries in which new WDEntity instances will be stored
    :param rec: A Reconciliator instance
    """
    first_batch = upload_batches[0]

    if ra.res not in first_batch:
        # Here we collect data needed for reconciliation:
        id_dict = extract_ids(ra)
        if id_dict_is_empty(id_dict):
            # No identifiers that could be used in the later reconciliation
            # process. We won't create this entity...
            return

        # Reconciliation:
        rec.reconciliate(ra.res, id_dict)
        match = rec.get_match(ra.res)

        if match is not None:
            # Successful reconciliation
            ra_entity = OrganizationWDEntity(qid=match, instance_of='Q386724')  # TODO: instance of 'work' (?)
            first_batch[ra.res] = ra_entity
            br_entity.publishers[idx] = ra_entity
        else:
            # Failed reconciliation
            ra_entity = OrganizationWDEntity(instance_of='Q386724')  # TODO: instance of 'work' (?)

            # Identifiers extraction:
            ra_entity.id_dict.update(id_dict)

            # Title extraction [P1476]:
            ra_entity.data['title'] = ra.get_name()

            # The end of the process:
            first_batch[ra.res] = ra_entity
            br_entity.publishers[idx] = ra_entity
