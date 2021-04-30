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
import unittest
from oc_ocdm.graph import GraphSet
from id_extractor import extract_ids


class TestIdExtractor(unittest.TestCase):

    def test_extract_ids(self):
        resp_agent = 'http://w3c.org/oc/meta/pa/999'
        g_set = GraphSet('http://w3c.org/oc/meta/')
        br = g_set.add_br(resp_agent)

        isbn = g_set.add_id(resp_agent)
        isbn.create_isbn('978-88-515-2159-2')

        orcid = g_set.add_id(resp_agent)
        orcid.create_orcid('0000-0002-1825-0097')

        wikidata = g_set.add_id(resp_agent)
        wikidata.create_wikidata('Q9')

        br.has_identifier(isbn)
        br.has_identifier(orcid)
        br.has_identifier(wikidata)

        result = extract_ids(br)
        self.assertIsNotNone(result)

        self.assertDictEqual(result, {'isbn13': '978-88-515-2159-2',
                                      'isbn10': '88-515-2159-X',  # this is automatically inferred
                                      'orcid': '0000-0002-1825-0097',
                                      'wikidata': 'Q9'})


if __name__ == '__main__':
    unittest.main()
