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

from utils.utils import split_range, split_range_optional


class TestUtils(unittest.TestCase):

    def test_split_range(self):
        with self.subTest('Range is None'):
            string = None
            result = split_range(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('', ''))
        with self.subTest('Range: 25-'):
            string = '25-'
            result = split_range(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('', ''))
        with self.subTest('Range: -25'):
            string = ' -25'
            result = split_range(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('', ''))
        with self.subTest('Range: 23-25'):
            string = '23-25'
            result = split_range(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('23', '25'))
        with self.subTest('Range: 220-25'):
            string = '220-25'
            result = split_range(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('220', '225'))
        with self.subTest('Range: 1, 25'):
            string = '1, 25'
            result = split_range(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('', ''))
        with self.subTest('Range: X-XV'):
            string = 'X-XV'
            result = split_range(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('', ''))

    def test_split_range_optional(self):
        with self.subTest('Range: 25-'):
            string = '25-'
            result = split_range_optional(string)
            self.assertIsNone(result)
        with self.subTest('Range: -25'):
            string = '-25'
            result = split_range_optional(string)
            self.assertIsNone(result)
        with self.subTest('Range: 23-25'):
            string = '23-25'
            result = split_range_optional(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('23', '25'))
        with self.subTest('Range: 220-25'):
            string = '220-25'
            result = split_range_optional(string)
            self.assertIsNotNone(result)

            self.assertTupleEqual(result, ('220', '225'))
        with self.subTest('Range: 1, 25'):
            string = '1, 25'
            result = split_range_optional(string)
            self.assertIsNone(result)
        with self.subTest('Range: X-XV'):
            string = 'X-XV'
            result = split_range_optional(string)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
