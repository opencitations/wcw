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
    from typing import Dict, Any

from oc_ocdm.support import get_datatype_from_iso_8601
from rdflib import XSD

from abc import ABC, abstractmethod


class WDEntity(ABC):
    """
    A generic Wikidata Entity. This is an abstract class and cannot be instantiated.
    """
    def __init__(self, qid: str = None):
        self.qid: str = qid
        self.data: Dict[str, Any] = {}
        self.id_dict: Dict[str, str] = {}

    @staticmethod
    def is_not_null(string: str) -> bool:
        """
        A predicate useful to know whether the given string is not null/empty.

        :param string: The string to be checked
        :return: True if the string is not None nor empty, False otherwise
        """
        return string is not None and string.strip() != ''

    @staticmethod
    def _fix_string(value, datatype):
        if datatype == 'string':
            # Some chars are reported to be problematic when using QuickStatements
            # via URLs.
            # See: https://www.wikidata.org/wiki/Help:QuickStatements#Add_simple_statement
            known_problematic_chars = {'_', '\"', ' ', '='}  # and maybe more...
            for char in known_problematic_chars:
                value = value.replace(char, '')

            # TODO: check if in the TSV QS v1 format we should also do value.replace('\"', '\"\"') !!!
            value = value.replace('\t', '')
            # value = value.replace('\"', '\"\"')
            value = '\"' + value + '\"'  # value = '\"\"\"' + value + '\"\"\"'

        elif datatype == 'datetime':
            dtype, date_str = get_datatype_from_iso_8601(value)
            if dtype == XSD.date:
                resolution = '11'  # day
                full_iso8601_datetime = date_str + 'T00:00:00Z'
            elif dtype == XSD.gYearMonth:
                resolution = '10'  # month
                full_iso8601_datetime = date_str + '-01T00:00:00Z'
            elif dtype == XSD.gYear:
                resolution = '9'  # year
                full_iso8601_datetime = date_str + '-01-01T00:00:00Z'
            else:
                raise ValueError(f'Given datetime value has an unknown resolution')
            value = '+' + full_iso8601_datetime + '/' + resolution

        elif datatype == 'wd_item':
            # Nothing to do here...
            pass
        else:
            raise ValueError(f'Given datatype is unknown: {datatype}. Supported datatypes are: '
                             f'[string, datetime, wd_item]')
        return value

    @staticmethod
    def statement(predicate: str, value: str, datatype: str = 'string', with_reference: bool = True) -> str:
        """
        Helper method that builds a TSV statement based on the arguments passed. It's able to construct
        a statement containing a predicate, a value and optionally a reference saying: 'stated in enwiki'.

        :param predicate: A string containing the predicate (ex. P236 for 'ISSN')
        :param value: A string containing the value associated with the predicate
        :param datatype: Either 'string', 'datetime' or 'wd_item'. In case of 'wd_item', a Wikidata ID is
        expected as the content of the 'value' argument
        :param with_reference: True if a reference to enwiki should be added to the statement, False otherwise
        :return: A string containing the requested TSV statement
        """
        value = WDEntity._fix_string(value, datatype)
        if with_reference:
            return '\t'.join(['LAST', predicate, value, 'S248', 'Q328'])
        else:
            return '\t'.join(['LAST', predicate, value])

    @staticmethod
    def ordered_statement(predicate: str, value: str, order_number: int, datatype: str = 'string',
                          with_reference: bool = True) -> str:
        """
        Helper method that builds a TSV statement based on the arguments passed. It's able to construct
        a statement containing a predicate, a value and optionally a reference saying: 'stated in enwiki'.
        Furthermore, with respect to 'statement', this method is capable of adding a statement qualifier
        saying 'series ordinal NUM'. Useful for creating statements about lists of authors, editors and
        publishers of a particular bibliographic resource.

        :param predicate: A string containing the predicate (ex. P236 for 'ISSN')
        :param value: A string containing the value associated with the predicate
        :param order_number: An integer number representing the ordering qualifier's value
        :param datatype: Either 'string', 'datetime' or 'wd_item'. In case of 'wd_item', a Wikidata ID is
        expected as the content of the 'value' argument
        :param with_reference: True if a reference to enwiki should be added to the statement, False otherwise
        :return: A string containing the requested TSV statement
        """
        if order_number < 0:
            raise ValueError('order_number must be greater or equal than zero!')

        value = WDEntity._fix_string(value, datatype)
        if with_reference:
            return '\t'.join(['LAST', predicate, value, 'P1545', str(order_number), 'S248', 'Q328'])
        else:
            return '\t'.join(['LAST', predicate, value, 'P1545', str(order_number)])

    @abstractmethod
    def stringify(self) -> str:
        """
        This method converts the information contained inside the WDEntity and it returns it in
        the form of a sequence of statements compatible with the TSV QuickStatements format.

        :return: A string containing the TSV statements ready to be interpreted by QuickStatements
        """
        raise NotImplementedError
