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
    from typing import Dict
    from rdflib import URIRef

from entities.WDEntity import WDEntity
from config import temp_TSV_batch_output_file


def upload_batch(entity_batch: Dict[URIRef, WDEntity]):
    """
    This function does the bulk-upload of the given batch of entities.
    Only entities without a Wikidata ID will be uploaded, because they weren't
    successfully reconciled (which means that, with some level of probability,
    they're entirely missing in Wikidata).

    PLEASE NOTE: this function was initially intended to actually do the bulk-upload
    through some kind of API or maybe through the use of the QuickStatements tool.
    Since, for various reasons, we didn't manage to implement such a behaviour within
    the constrained time limits of our grant, we did come up with the idea of letting the
    user to manually upload the data. This behaviour could be modified in a future review
    of this project.

      - As for now, the script exports a temporary TSV file with a fixed name in a particular folder
        (all of this is configurable inside config.py) and then pauses its execution waiting for a
        confirmation from the user.
      - The user should use the content of that file to bulk-upload the statements through the QuickStatements
        web interface and, when done, should follow the command line instructions to confirm that the upload
        was completed.
      - Since every time this function is called, that file would be overwritten, it's suggested that the user
        stored a copy of it somewhere else in his computer's filesystem.

    :param entity_batch: A dictionary representing the batch of WDEntity instances to be reconciled
    """
    print("> BATCH UPLOAD")
    print(f">> Temporary TSV batch file: {temp_TSV_batch_output_file}")
    print(">> The temporary TSV batch file is going to be overwritten.")
    print(">>")
    print(">> Would you like to proceed anyway?")
    input(">>> Press [ENTER] to proceed or [CTRL+C] to stop the execution of the entire process: ")
    input(">>> Please confirm (press ENTER again): ")
    with open(temp_TSV_batch_output_file, 'w', encoding='utf-8') as f:
        entity_list = list(entity_batch.values())
        for entity in entity_list:
            if not WDEntity.is_not_null(entity.qid):
                # QID is missing -> we need to create this entity
                statement_lines: str = entity.stringify() + '\n'
                f.write(statement_lines)
    print(">> The TSV file has been overwritten. Please manually upload it with the web interface"
          " of QuickStatements!")
    input(">>> Press [ENTER] when you're done to proceed or [CTRL+C] to stop the execution of the entire process: ")
    input(">>> Please confirm (press ENTER again): ")
