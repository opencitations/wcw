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
    from typing import Optional, Dict, Any

from OrganizationWDEntity import OrganizationWDEntity
from HumanWDEntity import HumanWDEntity
from WDEntity import WDEntity


class BibliographicWDEntity(WDEntity):
    """
    A Wikidata Entity representing a bibliographic resource.
    """

    ocdm_to_wikidata = {
        'instance_of': ('P31', 'wd_item'),
        'title': ('P1476', 'string'),
        'publication_date': ('P577', 'datetime'),
        'author_strings': ('P2093', 'string'),
        'authors': ('P50', 'wd_item'),
        'editors': ('P98', 'wd_item'),
        'publishers': ('P123', 'wd_item'),
        'venue': ('P1433', 'wd_item'),
        'volume': ('P478', 'string'),
        'pages': ('P304', 'string'),
        'issue': ('P433', 'string'),

        # Identifiers
        'doi': ('P356', 'string'),
        'pmid': ('P698', 'string'),
        'pmcid': ('P932', 'string'),
        'isbn10': ('P957', 'string'),
        'isbn13': ('P212', 'string')
    }

    def __init__(self, instance_of: str = None, qid: str = None):
        super(BibliographicWDEntity, self).__init__(qid=qid)
        self.venue: Optional[BibliographicWDEntity] = None
        self.authors: Dict[int, HumanWDEntity] = {}
        self.editors: Dict[int, HumanWDEntity] = {}
        self.publishers: Dict[int, OrganizationWDEntity] = {}

        self.data: Dict[str, Any] = {
            'instance_of': instance_of,
            'title': '',
            'publication_date': '',
            'author_strings': {},
            'authors': {},
            'editors': {},
            'publishers': {},
            'venue': '',
            'volume': '',
            'pages': '',
            'issue': ''
        }
        self.id_dict: Dict[str, str] = {
            'doi': '',
            'pmid': '',
            'pmcid': '',
            'issn': '',
            'isbn10': '',
            'isbn13': ''
        }

    def stringify(self) -> str:
        if self.venue is not None and self.is_not_null(self.venue.qid):
            self.data['venue'] = self.venue.qid

        for author_idx, author in self.authors.items():
            if author is not None:
                if self.is_not_null(author.qid):
                    self.data['authors'][author_idx] = author.qid
                else:
                    author_string = None
                    given_name = author.data['given_name']
                    family_name = author.data['family_name']
                    if self.is_not_null(given_name) and \
                            self.is_not_null(family_name):
                        author_string = given_name + ' ' + family_name
                    elif self.is_not_null(given_name):
                        author_string = given_name
                    elif self.is_not_null(family_name):
                        author_string = family_name

                    if self.is_not_null(author_string):
                        self.data['author_strings'][author_idx] = author_string

        for editor_idx, editor in self.editors.items():
            if editor is not None:
                if self.is_not_null(editor.qid):
                    self.data['editors'][editor_idx] = editor.qid
                else:
                    # Without a proper QID, we won't create this statement!
                    pass

        for publisher_idx, publisher in self.publishers.items():
            if publisher is not None:
                if self.is_not_null(publisher.qid):
                    self.data['publishers'][publisher_idx] = publisher.qid
                else:
                    # Without a proper QID, we won't create this statement!
                    pass

        # Statements creation:
        statements = ['CREATE']

        full_dict = {**self.data, **self.id_dict}
        for key, value in full_dict.items():
            if key == 'author_strings':
                for author_string_idx, author_string_val in value.items():
                    if author_string_idx >= 0 and self.is_not_null(author_string_val):
                        prop, datatype = self.ocdm_to_wikidata['author_strings']
                        # Add a statement containing an ordering qualifier:
                        statements.append(self.ordered_statement(prop, author_string_val, author_string_idx,
                                                                 datatype))
            elif key == 'authors':
                for author_idx, author_val in value.items():
                    if author_idx >= 0 and not self.is_not_null(author_val):
                        prop, datatype = self.ocdm_to_wikidata['authors']
                        # Add a statement containing an ordering qualifier:
                        statements.append(self.ordered_statement(prop, author_val, author_idx, datatype))
            else:
                if self.is_not_null(value) and key in self.ocdm_to_wikidata:
                    prop, datatype = self.ocdm_to_wikidata[key]
                    statements.append(self.statement(prop, value, datatype))

        return '\n'.join(statements)
