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
from id_utils.isbn_utils import isbn_normalize, isbn_length, isbn10_is_valid,\
                                isbn10_check_digit, from_isbn10_to_isbn13,\
                                isbn13_is_valid, isbn13_check_digit, from_isbn13_to_isbn10


class TestIsbnUtils(unittest.TestCase):

    def test_isbn_normalize(self):
        string = '-------------9\r78-3-1hjk6-148\n410-0------'
        result = isbn_normalize(string)
        self.assertIsNotNone(result)

        self.assertEqual(result, '978-3-16-148410-0')

    def test_isbn_length(self):
        with self.subTest("isbn10"):
            string = '3-16-148410-0'
            result = isbn_length(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, 10)
        with self.subTest("isbn13"):
            string = '978-3-16-148410-0'
            result = isbn_length(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, 13)

    def test_isbn10_is_valid(self):
        with self.subTest('isbn10 too long'):
            string = '978-3-16-148410-0'
            result = isbn10_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('isbn10 too short'):
            string = '148410-0'
            result = isbn10_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Wrong check digit'):
            string = '88-515-2159-3'
            result = isbn10_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Valid isbn10'):
            string = '88-515-2159-X'
            result = isbn10_is_valid(string)
            self.assertIsNotNone(result)

            self.assertTrue(result)

    def test_isbn10_check_digit(self):
        with self.subTest('isbn10 1'):
            string = '0-521-22151-X'
            result = isbn10_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, 'X')
        with self.subTest('isbn10 2'):
            string = '0-521-29366-9'
            result = isbn10_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '9')
        with self.subTest('isbn10 3'):
            string = '88-515-2159-X'
            result = isbn10_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, 'X')

    def test_from_isbn10_to_isbn13(self):
        string = '88-515-2159-X'
        result = from_isbn10_to_isbn13(string)
        self.assertIsNotNone(result)

        self.assertEqual(result, '978-88-515-2159-2')

    def test_isbn13_is_valid(self):
        with self.subTest('isbn13 too long'):
            string = '978-3-16-148410-0125'
            result = isbn13_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('isbn13 too short'):
            string = '148410-0'
            result = isbn13_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Wrong check digit'):
            string = '978-3-16-148410-5'
            result = isbn13_is_valid(string)
            self.assertIsNotNone(result)

            self.assertFalse(result)
        with self.subTest('Valid isbn13'):
            string = '978-3-16-148410-0'
            result = isbn13_is_valid(string)
            self.assertIsNotNone(result)

            self.assertTrue(result)

    def test_isbn13_check_digit(self):
        with self.subTest('isbn13 1'):
            string = '978-1-56619-909-4'
            result = isbn13_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '4')
        with self.subTest('isbn13 2'):
            string = '978-1-4028-9462-6'
            result = isbn13_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '6')
        with self.subTest('isbn13 3'):
            string = '978-1-86197-876-9'
            result = isbn13_check_digit(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '9')

    def test_from_isbn13_to_isbn10(self):
        with self.subTest('isbn13 that starts with 978'):
            string = '978-88-515-2159-2'
            result = from_isbn13_to_isbn10(string)
            self.assertIsNotNone(result)

            self.assertEqual(result, '88-515-2159-X')
        with self.subTest('isbn13 that doesn\'t start with 978'):
            string = '456-88-515-2159-2'
            result = from_isbn13_to_isbn10(string)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
