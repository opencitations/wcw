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
import unicodedata
import re
import sys

# Control categories of Unicode (there are also Cs (surrogate), Co (private-use) and Cn (unassigned))
categories = {'Cc', 'Cf'}
control_chars = []
for i in range(sys.maxunicode):
    c = chr(i)
    if unicodedata.category(c) in categories:
        control_chars.append(c)
control_chars = ''.join(control_chars)
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def remove_invisible_chars(s):
    # This also removes ASCII characters that are invisible like \n, \t and \r !
    return control_char_re.sub('', s)
