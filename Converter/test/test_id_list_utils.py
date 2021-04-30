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
from utils.id_list_utils import invalid_brackets, clean_id_list_string,\
                                parse_id_list, parse_id_list_repeated_schemes

class TestIdUtils(unittest.TestCase):

    def test_invalid_brackets(self):
        self.assertTrue(invalid_brackets(-1, 8))
        self.assertTrue(invalid_brackets(8, -1))
        self.assertTrue(invalid_brackets(8, 8))
        self.assertTrue(invalid_brackets(8, 6))
        self.assertFalse(invalid_brackets(5, 10))

    def test_clean_id_list_string(self):
        result = clean_id_list_string('  isbn=def, \u0001\n\rissn=pqr  ')
        self.assertIsNotNone(result)

        self.assertEqual(result, 'isbn=def, issn=pqr')

    def test_parse_id_list(self):
        with self.subTest('Valid string'):
            result = parse_id_list('{doi=xyz, isbn=abc, doi=PQR}')
            self.assertIsNotNone(result)

            self.assertDictEqual(result, {'doi': 'PQR', 'isbn': 'abc'})

        with self.subTest('Invalid strings (ignore_errors=False)'):
            self.assertRaises(ValueError, parse_id_list, 'doi=xyz,} isbn=abc, doi=PQR{', False)
            self.assertRaises(ValueError, parse_id_list, '{doi=xy=z, isbn=abc, doi=PQR}', False)
            self.assertRaises(ValueError, parse_id_list, '{asgr=xxx, poiaf=yyy}', False)

        with self.subTest('Invalid strings (ignore_errors=True)'):
            self.assertDictEqual(parse_id_list('doi=xyz,{ isbn=abc, doi=PQR{', True), {})
            self.assertDictEqual(parse_id_list('{doi=xy=z, isbn=abc, doi=PQR}', True), {})
            self.assertDictEqual(parse_id_list('{asgr=xxx, poiaf=yyy}', True), {})

    def test_parse_id_list_repeated_schemes(self):
        with self.subTest('Valid string'):
            result = parse_id_list_repeated_schemes('tmp:xyz tmp:abc meta:PQR')
            self.assertIsNotNone(result)

            self.assertDictEqual(result, {'tmp': ['xyz', 'abc'], 'meta': ['PQR']})

        with self.subTest('Invalid strings (ignore_errors=False)'):
            self.assertRaises(ValueError, parse_id_list_repeated_schemes, 'tmp:xyz tmp:abc metaPQR', False)
            self.assertRaises(ValueError, parse_id_list_repeated_schemes, 'doi:xyz issn:abc doi:PQR', False)

        with self.subTest('Invalid strings (ignore_errors=True)'):
            self.assertDictEqual(parse_id_list_repeated_schemes('tmp:xyz tmp:abc metaPQR', True), {})
            self.assertDictEqual(parse_id_list_repeated_schemes('doi:xyz issn:abc doi:PQR', True), {})


if __name__ == '__main__':
    unittest.main()
