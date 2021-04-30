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
from utils.authors_utils import extract_author_name, invalid_brackets, unify_duplicated_equal_signs,\
                                clean_author_string, get_author_dict, parse_authors


class TestAuthorsUtils(unittest.TestCase):

    def test_extract_author_name(self):
        with self.subTest('only first'):
            result = extract_author_name({'first': 'Jo,hn'})
            self.assertIsNotNone(result)

            self.assertEqual(result, ', John')
        with self.subTest('only last'):
            result = extract_author_name({'last': 'P.'})
            self.assertIsNotNone(result)

            self.assertEqual(result, 'P., ')
        with self.subTest('first and last'):
            result = extract_author_name({'first': 'Jo,hn', 'last': 'P.'})
            self.assertIsNotNone(result)

            self.assertEqual(result, 'P., John')
        with self.subTest('link with comma'):
            result = extract_author_name({'link': 'John, P.'})
            self.assertIsNotNone(result)

            self.assertEqual(result, 'John, P.')
        with self.subTest('link without comma'):
            result = extract_author_name({'link': 'John P.'})
            self.assertIsNone(result)

    def test_invalid_brackets(self):
        self.assertTrue(invalid_brackets(-1, 8))
        self.assertTrue(invalid_brackets(8, -1))
        self.assertTrue(invalid_brackets(8, 8))
        self.assertTrue(invalid_brackets(8, 6))
        self.assertFalse(invalid_brackets(5, 10))

    def test_unify_duplicated_equal_signs(self):
        result = unify_duplicated_equal_signs('abc===def, mno= =pqr, stv==q==  =')
        self.assertIsNotNone(result)

        self.assertEqual(result, 'abc=def, mno=pqr, stv=q=')

    def test_clean_author_string(self):
        result = clean_author_string('  abc===[def, \u0001\n\rmno= ]=pqr, stv==q==]  =   ')
        self.assertIsNotNone(result)

        self.assertEqual(result, 'abc=def, mno=pqr, stv=q=')

    def test_get_author_dict(self):
        result = get_author_dict('first=Clark, last===Kent, link==Superman')
        self.assertIsNotNone(result)

        self.assertDictEqual(result, {'first': 'Clark', 'last': 'Kent', 'link': 'Superman'})

    def test_parse_authors(self):
        with self.subTest('Valid string'):
            result = parse_authors('[{first=Clark, last===Kent, link==Superman}, {first=Albert, last=Einstein}]')
            self.assertIsNotNone(result)

            self.assertListEqual(result, [{'first': 'Clark', 'last': 'Kent', 'link': 'Superman'},
                                          {'first': 'Albert', 'last': 'Einstein'}])
        with self.subTest('Invalid strings (ignore_errors=False)'):
            self.assertRaises(ValueError, parse_authors, '{first=Clark,] [last===Kent, link==Superman},'
                                                         ' {first=Albert, last=Einstein}]', False)
            self.assertRaises(ValueError, parse_authors, '[{}, {first=Clark, last=,==Kent, link==Superman},'
                                                         ' {first=Albert, last=Einstein}]', False)
            self.assertRaises(ValueError, parse_authors, '[]', False)

        with self.subTest('Invalid strings (ignore_errors=True)'):
            self.assertListEqual(parse_authors('{first=Clark, [last===Kent, link==Superman},'
                                               ' {first=Albert, last=Einstein}]', True), [])
            self.assertListEqual(parse_authors('[{}, {first=Clark, last=,==Kent, link==Superman},'
                                               ' {first=Albert, last=Einstein}]', True), [])
            self.assertListEqual(parse_authors('[]', True), [])


if __name__ == '__main__':
    unittest.main()
