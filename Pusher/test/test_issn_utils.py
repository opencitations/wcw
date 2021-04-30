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
from id_utils.issn_utils import normalize_issn, issn_is_valid, issn_check_digit


class TestIssnUtils(unittest.TestCase):

    def test_normalize_issn(self):
        string = '0s 0\n00-23!amnsfb45'
        result = normalize_issn(string)
        self.assertIsNotNone(result)

        self.assertEqual(result, '0000-2345')

    def test_issn_is_valid(self):
        with self.subTest('Missing dash'):
            string = '00001234'
            result = issn_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('ISSN too short'):
            string = '000-000'
            result = issn_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('ISSN too long'):
            string = '0000-0000-0000-0000'
            result = issn_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('X not in the last position'):
            string = '0000-00X0'
            result = issn_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Dash in the wrong position'):
            string = '00-00000'
            result = issn_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Wrong check digit'):
            string = '2049-363X'
            result = issn_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Valid ISSN'):
            string = '2049-3630'
            result = issn_is_valid(string)
            self.assertIsNotNone(result)

            self.assertTrue(result)

    def test_issn_check_digit(self):
        with self.subTest('ISSN 1'):
            string = '2049-3630'
            result = issn_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '0')
        with self.subTest('ISSN 2'):
            string = '0028-0836'
            result = issn_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '6')
        with self.subTest('ISSN 3'):
            string = '0954-349X'
            result = issn_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, 'X')


if __name__ == '__main__':
    unittest.main()
