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

from WDEntity import WDEntity


class EnWikiPageWDEntity(WDEntity):
    """
    A Wikidata Entity representing a Wikipedia page.
    """

    ocdm_to_wikidata = {
        'instance_of': ('P31', 'wd_item'),
        'title': ('P1476', 'string'),

        # Identifiers
        'wikipedia': (None, 'string')  # TODO: a new property must be created in Wikidata
    }

    def __init__(self, qid: str = None):
        super(EnWikiPageWDEntity, self).__init__(qid=qid)
        self.sitelink: Optional[str] = None
        self.data: Dict[str, Any] = {
            'instance_of': 'Q50081413',
            'title': ''
        }
        self.id_dict: Dict[str, str] = {
            'wikipedia': ''
        }

    def stringify(self) -> str:
        if self.is_not_null(self.qid):
            return ''
        else:
            statements = ['CREATE']

            if self.is_not_null(self.sitelink):
                # It's a Wikipedia page from enwiki!
                # We need to add the proper sitelink!
                statements.append(self.statement('Senwiki', self.sitelink, 'string', with_reference=False))

            full_dict = {**self.data, **self.id_dict}
            for key, value in full_dict.items():
                if self.is_not_null(value) and key in self.ocdm_to_wikidata:
                    prop, datatype = self.ocdm_to_wikidata[key]
                    statements.append(self.statement(prop, value, datatype))

            return '\n'.join(statements)
