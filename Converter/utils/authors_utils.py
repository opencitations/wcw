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
    from typing import List, Dict, Optional, Set

from utils.invisible_chars import remove_invisible_chars


def stringify_authors(authors_list: List[Dict[str, str]]) -> str:
    forbidden_chars: Set[str] = {':', ';', '[', ']'}  # these chars are used as delimiters in the output format
    is_first_author: bool = True
    converted_string: str = ''  # we start from an empty string
    for author in authors_list:
        author_name: Optional[str] = extract_author_name(author)

        if author_name is not None:
            for char in forbidden_chars:
                author_name = author_name.replace(char, '')

            if not is_first_author:
                # After the first round, always add a semicolon to separate authors
                converted_string += "; "

            converted_string += author_name
            is_first_author = False
    return converted_string


def extract_author_name(author: Dict[str, str]) -> Optional[str]:
    first = 'first' in author
    last = 'last' in author
    link = 'link' in author

    author_name = None
    if first and last:
        lastname = author['last'].replace(',', '')
        firstname = author['first'].replace(',', '')
        author_name = f"{lastname}, {firstname}"
    elif first:
        firstname = author['first'].replace(',', '')
        author_name = f", {firstname}"
    elif last:
        lastname = author['last'].replace(',', '')
        author_name = f"{lastname}, "
    elif link:
        if ',' in author['link']:
            author_name = f"{author['link']}"
        else:
            author_name = None

    return author_name


def invalid_brackets(first: int, last: int) -> bool:
    return first < 0 or last < 0 or first >= last


def unify_duplicated_equal_signs(s: str) -> str:
    """ 
    Removes repeated equal signs only if they are one after the other
    or if they are separated by spaces.
    Example: 'abc===def, mno= =pqr, stv==q==  =' --> 'abc=def, mno=pqr, stv=q='
    """
    sequence_started = False
    new_string = []
    for char in s:
        if not sequence_started:
            new_string.append(char)
            if char == '=':
                sequence_started = True
        else:
            if char != '=' and not char.isspace():
                sequence_started = False
                new_string.append(char)
    return ''.join(new_string)


def clean_author_string(s: str) -> str:
    # '[' and ']' must be removed because they are interpreted by 'meta' as ID enclosing symbols!
    s = s.replace('[', '')
    s = s.replace(']', '')
    s = remove_invisible_chars(s)
    s = unify_duplicated_equal_signs(s)
    return s.strip()


def get_author_dict(author: str) -> Dict[str, str]:
    author = clean_author_string(author)
    tokens = author.split('=')
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
        return {}
    
    author_dict = {}
    known_keys = ['link', 'first', 'last']
    for i in range(0, len(all_tokens), 2):
        key = all_tokens[i].lower().strip()
        value = all_tokens[i+1].strip()
        if key in known_keys and value != '':
            author_dict[key] = value
    
    return author_dict


def parse_authors(authors: str, ignore_errors: bool = True) -> List[Dict[str, str]]:
    # I don't want to lose a reference to the initial 'authors' value
    s = authors
    
    if s is None:
        return []
    
    s = s.strip()
    if s == '':
        return []
    
    opening_bracket = s.find('[')
    closing_bracket = s.rfind(']')  # start searching from the end of the string
    if invalid_brackets(opening_bracket, closing_bracket):
        # String is malformed, return nothing
        if ignore_errors:
            return []
        else:
            raise ValueError(f'Malformed string (misplaced square brackets): {authors}')
    
    s = s[opening_bracket + 1: closing_bracket]
    
    authors_list = []
    
    # Find first 'author' structure
    opening_obj = s.find('{')
    closing_obj = s.find('}')
    while not invalid_brackets(opening_obj, closing_obj):  # foreach 'author' structure
        author = s[opening_obj + 1: closing_obj]  # by construction, it cannot contain '{' or '}'
        author_dict = get_author_dict(author)
        if len(author_dict) > 0:
            authors_list.append(author_dict)
        else:
            if ignore_errors:
                return []
            else:
                raise ValueError(f'Malformed string (at least one of the author structures is invalid): {authors}')
        
        # Find next 'author' structure
        s = s[closing_obj + 1:]  # 'closing_obj' is the index of '}'
        opening_obj = s.find('{')
        closing_obj = s.find('}')
    
    if len(authors_list) == 0:
        if ignore_errors:
            return []
        else:
            raise ValueError(f'Malformed string (no author info was extracted): {authors}')
    return authors_list
