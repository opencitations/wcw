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
from id_utils.orcid_utils import normalize_orcid, orcid_is_valid, orcid_check_digit


class TestOrcidUtils(unittest.TestCase):

    def test_normalize_orcid(self):
        string = '0s 0\n00-23!amnsfb45-4567-___5678'
        result = normalize_orcid(string)
        self.assertIsNotNone(result)

        self.assertEqual(result, '0000-2345-4567-5678')

    def test_orcid_is_valid(self):
        with self.subTest('Missing first dash'):
            string = '00001234-5678-9876'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Missing second dash'):
            string = '0000-12345678-9876'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Missing third dash'):
            string = '0000-1234-56789876'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('ORCID too short'):
            string = '0000-0000'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('ORCID too long'):
            string = '0000-0000-0000-0000-0000'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('X not in the last position'):
            string = '0000-00X0-0000-0000'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Dash in the wrong position'):
            string = '00-00000-0-00000000'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Wrong check digit'):
            string = '0000-0002-1825-0093'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Valid ORCID'):
            string = '0000-0002-1825-0097'
            result = orcid_is_valid(string)
            self.assertIsNotNone(result)

            self.assertTrue(result)

    def test_orcid_check_digit(self):
        with self.subTest('ORCID 1'):
            string = '0000-0002-1825-0097'
            result = orcid_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '7')
        with self.subTest('ORCID 2'):
            string = '0000-0001-2345-6789'
            result = orcid_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '9')
        with self.subTest('ORCID 3'):
            string = '0000-0002-1694-233X'
            result = orcid_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, 'X')


if __name__ == '__main__':
    unittest.main()
