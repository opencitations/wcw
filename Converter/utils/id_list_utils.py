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
    from typing import Dict, Set

from utils.invisible_chars import remove_invisible_chars


allowed_id_schemes = {'doi', 'isbn', 'issn', 'pmc', 'pmid'}


def stringify_id_list(id_info: Dict[str, str]) -> str:
    forbidden_chars: Set[str] = {':', ';', ' '}  # these chars are used as delimiters in the output format
    is_first_id: bool = True
    converted_string: str = ''  # we start from an empty string
    for scheme, identifier in id_info.items():
        # Beware that 'identifier' could be a float('nan') value in case a particular 'scheme' value is missing:
        if scheme is not None and identifier is not None and type(identifier) == str:
            for char in forbidden_chars:
                scheme = scheme.replace(char, '')
                identifier = identifier.replace(char, '')

            if not is_first_id:
                # After the first round, always add a space to separate identifiers
                converted_string += " "

            converted_string += f"{scheme}:{identifier}"
            is_first_id = False
    return converted_string


def invalid_brackets(first, last):
    return first < 0 or last < 0 or first >= last


def clean_id_list_string(s):
    s = remove_invisible_chars(s)
    return s.strip()


def parse_id_list(id_list, ignore_errors=True):
    # I don't want to lose a reference to the initial 'ID_list' value
    s = id_list
    
    if s is None:
        return {}
    
    s = s.strip()
    if s == '':
        return {}
    
    opening_bracket = s.find('{')
    closing_bracket = s.rfind('}')  # start searching from the end of the string
    if invalid_brackets(opening_bracket, closing_bracket):
        # String is malformed, return nothing
        if ignore_errors:
            return {}
        else:
            raise ValueError(f'Malformed string (misplaced curly brackets): {id_list}')
    
    s = s[opening_bracket + 1: closing_bracket]
    
    s = clean_id_list_string(s)
    tokens = s.split('=')
    if len(tokens) <= 1:
        return {}
    
    all_tokens = [tokens[0]]  # insert first token
    for i in range(1, len(tokens) - 1):
        # It's fundamentally important that the string
        # is split by the last ',' char: value tokens
        # can contain one or more ','!
        sub_tokens = tokens[i].rsplit(',', maxsplit=1)
        all_tokens.extend(sub_tokens)
    all_tokens.append(tokens[-1])  # insert last token
    
    # I don't try to parse tokens if I cannot safely distinguish
    # between keys and values. In case of values containing '=' chars,
    # I would risk to accept only a part of them, possibly changing their meaning.
    if len(all_tokens) % 2 != 0:
        if ignore_errors:
            return {}
        else:
            raise ValueError(f'Malformed string (at least one of the ID structures is invalid): {id_list}')
    
    id_info = {}
    for i in range(0, len(all_tokens), 2):
        key = all_tokens[i].lower().strip()
        value = all_tokens[i+1].strip()
        if key != '' and value != '' and key in allowed_id_schemes:
            # In case of two or more 'scheme:id' couples with the same 'scheme',
            # only the last 'id' value is kept for that particular 'scheme'.
            # With our input data it seems like it never happens, anyway...
            id_info[key] = value
    
    if len(id_info) == 0:
        if ignore_errors:
            return {}
        else:
            raise ValueError(f'Malformed string (no ID info was extracted): {id_list}')
    return id_info


def parse_id_list_repeated_schemes(id_list, ignore_errors=True):
    # I don't want to lose a reference to the initial 'ID_list' value
    s = id_list

    if s is None:
        return {}

    s = s.strip()
    if s == '':
        return {}

    s = clean_id_list_string(s)
    tokens = s.split(' ')
    if len(tokens) <= 1:
        return {}

    all_tokens = []
    for i in range(len(tokens)):
        # It's fundamentally important that the string
        # is split by the last ',' char: value tokens
        # can contain one or more ','!
        sub_tokens = tokens[i].rsplit(':', maxsplit=1)
        all_tokens.extend(sub_tokens)

    # I don't try to parse tokens if I cannot safely distinguish
    # between keys and values. In case of values containing '=' chars,
    # I would risk to accept only a part of them, possibly changing their meaning.
    if len(all_tokens) % 2 != 0:
        if ignore_errors:
            return {}
        else:
            raise ValueError(f'Malformed string (at least one of the ID structures is invalid): {id_list}')

    id_info = {}
    for i in range(0, len(all_tokens), 2):
        key = all_tokens[i].lower().strip()
        value = all_tokens[i + 1].strip()
        if key != '' and value != '' and key in {'tmp', 'meta'}:
            if key not in id_info:
                id_info[key] = []
            id_info[key].append(value)

    if len(id_info) == 0:
        if ignore_errors:
            return {}
        else:
            raise ValueError(f'Malformed string (no ID info was extracted): {id_list}')
    return id_info
