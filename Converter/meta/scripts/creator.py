import re

from oc_ocdm.support import create_date
from rdflib import URIRef
from oc_ocdm.graph import GraphSet

from meta.lib.conf import resp_agent


class Creator(object):
    def __init__(self, data, base_iri, info_dir, ra_index, br_index, re_index_csv, ar_index_csv, vi_index):
        self.url = base_iri

        self.setgraph = GraphSet(self.url, info_dir, "", wanted_label=False)

        self.ra_index = self.indexer_id(ra_index)

        self.br_index = self.indexer_id(br_index)

        self.re_index = self.index_re(re_index_csv)

        self.ar_index = self.index_ar(ar_index_csv)

        self.vi_index = vi_index
        self.data = data

    def creator(self, source=None):
        self.src = source
        for row in self.data:
            self.row_meta = ""
            ids = row['id']
            title = row['title']
            authors = row['author']
            pub_date = row['pub_date']
            venue = row['venue']
            vol = row['volume']
            issue = row['issue']
            page = row['page']
            self.type = row['type']
            publisher = row['publisher']
            editor = row['editor']

            self.venue_graph = None
            self.vol_graph = None
            self.issue_graph = None

            self.id_action(ids)
            self.title_action(title)
            self.author_action(authors)
            self.pub_date_action(pub_date)
            self.vvi_action(venue, vol, issue)
            self.page_action(page)
            self.type_action(self.type)
            if publisher:
                self.publisher_action(publisher)
            if editor:
                self.editor_action(editor)

        return self.setgraph

    @staticmethod
    def index_re(id_index):
        index = dict()
        for row in id_index:
            index[row["br"]] = row["re"]
        return index

    @staticmethod
    def index_ar(id_index):
        index = dict()
        for row in id_index:
            index[row["meta"]] = dict()
            index[row["meta"]]["author"] = Creator.ar_worker(row["author"])
            index[row["meta"]]["editor"] = Creator.ar_worker(row["editor"])
            index[row["meta"]]["publisher"] = Creator.ar_worker(row["publisher"])
        return index

    @staticmethod
    def ar_worker(s):
        if s:
            ar_dict = dict()
            couples = s.split("; ")
            for c in couples:
                cou = c.split(", ")
                ar_dict[cou[1]] = cou[0]
            return ar_dict
        else:
            return dict()

    @staticmethod
    def indexer_id(csv_index):
        index = dict()
        index['crossref'] = dict()
        index["doi"] = dict()
        index["issn"] = dict()
        index["isbn"] = dict()
        index["orcid"] = dict()
        index["pmid"] = dict()
        index['pmcid'] = dict()
        index['url'] = dict()
        index['viaf'] = dict()
        index['wikidata'] = dict()
        index['wikipedia'] = dict()

        for row in csv_index:
            if row["id"].startswith("crossref"):
                identifier = row["id"].replace('crossref:', '')
                index['crossref'][identifier] = row["meta"]

            elif row["id"].startswith("doi"):
                identifier = row["id"].replace('doi:', '')
                index['doi'][identifier] = row["meta"]

            elif row["id"].startswith("issn"):
                identifier = row["id"].replace('issn:', '')
                index['issn'][identifier] = row["meta"]

            elif row["id"].startswith("isbn"):
                identifier = row["id"].replace('isbn:', '')
                index['isbn'][identifier] = row["meta"]

            elif row["id"].startswith("orcid"):
                identifier = row["id"].replace('orcid:', '')
                index['orcid'][identifier] = row["meta"]

            elif row["id"].startswith("pmid"):
                identifier = row["id"].replace('pmid:', '')
                index['pmid'][identifier] = row["meta"]

            elif row["id"].startswith("pmcid"):
                identifier = row["id"].replace('pmcid:', '')
                index['pmcid'][identifier] = row["meta"]

            elif row["id"].startswith("url"):
                identifier = row["id"].replace('url:', '')
                index['url'][identifier] = row["meta"]

            elif row["id"].startswith("viaf"):
                identifier = row["id"].replace('viaf:', '')
                index['viaf'][identifier] = row["meta"]

            elif row["id"].startswith("wikidata"):
                identifier = row["id"].replace('wikidata:', '')
                index['wikidata'][identifier] = row["meta"]

            elif row["id"].startswith("wikipedia"):
                identifier = row["id"].replace('wikipedia:', '')
                index['wikipedia'][identifier] = row["meta"]

        return index

    def id_action(self, ids):
        idslist = re.split(r'\s+', ids)

        # publication id
        for identifier in idslist:
            if "meta:" in identifier:
                identifier = identifier.replace("meta:", "")
                self.row_meta = identifier.replace("br/", "")
                url = URIRef(self.url + identifier)
                self.br_graph = self.setgraph.add_br(resp_agent, source=self.src, res=url)

        for identifier in idslist:
            self.id_creator(self.br_graph, identifier, ra=False)

    def title_action(self, title):
        if title:
            self.br_graph.has_title(title)

    def author_action(self, authors):
        if authors:
            authorslist = re.split(r'\s*;\s*(?=[^]]*(?:\[|$))', authors)

            aut_role_list = list()
            for aut in authorslist:
                aut_id = re.search(r'\[\s*(.*?)\s*]', aut).group(1)
                aut_id_list = aut_id.split(" ")

                for identifier in aut_id_list:
                    if "meta:" in identifier:
                        identifier = str(identifier).replace('meta:', "")
                        url = URIRef(self.url + identifier)
                        aut_meta = identifier.replace('ra/', "")
                        pub_aut = self.setgraph.add_ra(resp_agent, source=self.src, res=url)
                        author_name = re.search(r'(.*?)\s*\[.*?]', aut).group(1)
                        if "," in author_name:
                            author_name_splitted = re.split(r'\s*,\s*', author_name)
                            firstName = author_name_splitted[1]
                            lastName = author_name_splitted[0]
                            if firstName.strip():
                                pub_aut.has_given_name(firstName)
                            pub_aut.has_family_name(lastName)
                        else:
                            pub_aut.has_name(author_name)

                # lists of authors' IDs
                for identifier in aut_id_list:
                    self.id_creator(pub_aut, identifier, ra=True)

                # Author ROLE
                AR = self.ar_index[self.row_meta]["author"][aut_meta]
                ar_id = "ar/" + str(AR)
                url_ar = URIRef(self.url + ar_id)
                pub_aut_role = self.setgraph.add_ar(resp_agent, source=self.src, res=url_ar)
                pub_aut_role.create_author()
                self.br_graph.has_contributor(pub_aut_role)
                pub_aut_role.is_held_by(pub_aut)
                aut_role_list.append(pub_aut_role)
                if len(aut_role_list) > 1:
                    aut_role_list[aut_role_list.index(pub_aut_role)-1].has_next(pub_aut_role)

    def pub_date_action(self, pub_date):
        if pub_date:
            datelist = list()
            datesplit = pub_date.split("-")
            if datesplit:
                for x in datesplit:
                    datelist.append(int(x))
            else:
                datelist.append(int(pub_date))
            str_date = create_date(datelist)
            self.br_graph.has_pub_date(str_date)

    def vvi_action(self, venue, vol, issue):

        if venue:
            venue_id = re.search(r'\[\s*(.*?)\s*]', venue).group(1)
            venue_id_list = venue_id.split(" ")

            for identifier in venue_id_list:
                if "meta:" in identifier:
                    ven_id = str(identifier).replace("meta:", "")
                    url = URIRef(self.url + ven_id)
                    venue_title = re.search(r'(.*?)\s*\[.*?]', venue).group(1)
                    self.venue_graph = self.setgraph.add_br(resp_agent, source=self.src, res=url)
                    if self.type == "journal article" or self.type == "journal volume" or self.type == "journal issue":
                        self.venue_graph.create_journal()
                    elif self.type == "book chapter" or self.type == "book part":
                        self.venue_graph.create_book()
                    elif self.type == "proceedings article":
                        self.venue_graph.create_proceedings()
                    elif self.type == "report":
                        self.venue_graph.create_report_series()
                    elif self.type == "standard":
                        self.venue_graph.create_standard_series()

                    self.venue_graph.has_title(venue_title)

            for identifier in venue_id_list:
                self.id_creator(self.venue_graph, identifier, ra=False)

        if (self.type == "journal article" or self.type == "journal issue") and vol:

            meta_ven = ven_id.replace("br/", "")
            vol_meta = self.vi_index[meta_ven]["volume"][vol]["id"]
            vol_meta = "br/" + vol_meta
            url = URIRef(self.url + vol_meta)
            self.vol_graph = self.setgraph.add_br(resp_agent, source=self.src, res=url)
            self.vol_graph.create_volume()
            self.vol_graph.has_number(vol)

        if self.type == "journal article" and issue:

            meta_ven = ven_id.replace("br/", "")
            if vol:
                iss_meta = self.vi_index[meta_ven]["volume"][vol]["issue"][issue]["id"]
            else:
                iss_meta = self.vi_index[meta_ven]["issue"][issue]["id"]

            iss_meta = "br/" + iss_meta
            url = URIRef(self.url + iss_meta)
            self.issue_graph = self.setgraph.add_br(resp_agent, source=self.src, res=url)
            self.issue_graph.create_issue()
            self.issue_graph.has_number(issue)

        if venue and vol and issue:
            self.br_graph.is_part_of(self.issue_graph)
            self.issue_graph.is_part_of(self.vol_graph)
            self.vol_graph.is_part_of(self.venue_graph)

        elif venue and vol and not issue:
            self.br_graph.is_part_of(self.vol_graph)
            self.vol_graph.is_part_of(self.venue_graph)

        elif venue and not vol and not issue:
            self.br_graph.is_part_of(self.venue_graph)

        elif venue and not vol and issue:
            self.br_graph.is_part_of(self.issue_graph)
            self.issue_graph.is_part_of(self.venue_graph)

    def page_action(self, page):
        if page:
            res_em = self.re_index[self.row_meta]
            re_id = "re/" + str(res_em)
            url_re = URIRef(self.url + re_id)
            form = self.setgraph.add_re(resp_agent, source=self.src, res=url_re)
            form.has_starting_page(page)
            form.has_ending_page(page)
            self.br_graph.has_format(form)

    def type_action(self, entity_type):
        if entity_type == "archival document":
            self.br_graph.create_archival_document()
        elif entity_type == "book":
            self.br_graph.create_book()
        elif entity_type == "book chapter":
            self.br_graph.create_book_chapter()
        elif entity_type == "book part":
            self.br_graph.create_book_part()
        elif entity_type == "book section":
            self.br_graph.create_book_section()
        elif entity_type == "book series":
            self.br_graph.create_book_series()
        elif entity_type == "book set":
            self.br_graph.create_book_set()
        elif entity_type == "data file":
            self.br_graph.create_dataset()
        elif entity_type == "dissertation":
            self.br_graph.create_dissertation()
        elif entity_type == "journal":
            self.br_graph.create_journal()
        elif entity_type == "journal article":
            self.br_graph.create_journal_article()
        elif entity_type == "journal issue":
            self.br_graph.create_issue()
        elif entity_type == "journal volume":
            self.br_graph.create_volume()
        elif entity_type == "proceedings article":
            self.br_graph.create_proceedings_article()
        elif entity_type == "proceedings":
            self.br_graph.create_proceedings()
        elif entity_type == "reference book":
            self.br_graph.create_reference_book()
        elif entity_type == "reference entry":
            self.br_graph.create_reference_entry()
        elif entity_type == "report":
            self.br_graph.create_report()
        elif entity_type == "standard":
            self.br_graph.create_standard()
        elif entity_type == "series":
            self.br_graph.create_series()

    def publisher_action(self, publisher):

        publ_id = re.search(r'\[\s*(.*?)\s*]', publisher).group(1)
        publ_id_list = publ_id.split(" ")

        for identifier in publ_id_list:
            if "meta:" in identifier:
                identifier = str(identifier).replace("meta:", "")
                pub_meta = identifier.replace("ra/", "")
                url = URIRef(self.url + identifier)
                publ_name = re.search(r'(.*?)\s*\[.*?]', publisher).group(1)
                publ = self.setgraph.add_ra(resp_agent, source=self.src, res=url)
                publ.has_name(publ_name)

        for identifier in publ_id_list:
            self.id_creator(publ, identifier, ra=True)

        # publisherRole
        AR = self.ar_index[self.row_meta]["publisher"][pub_meta]
        ar_id = "ar/" + str(AR)
        url_ar = URIRef(self.url + ar_id)
        publ_role = self.setgraph.add_ar(resp_agent, source=self.src, res=url_ar)
        publ_role.create_publisher()
        self.br_graph.has_contributor(publ_role)
        publ_role.is_held_by(publ)

    def editor_action(self, editor):
        editorslist = re.split(r'\s*;\s*(?=[^]]*(?:\[|$))', editor)

        edit_role_list = list()
        for ed in editorslist:
            ed_id = re.search(r'\[\s*(.*?)\s*]', ed).group(1)
            ed_id_list = ed_id.split(" ")

            for identifier in ed_id_list:
                if "meta:" in identifier:
                    identifier = str(identifier).replace("meta:", "")
                    ed_meta = identifier.replace("ra/", "")
                    url = URIRef(self.url + identifier)
                    pub_ed = self.setgraph.add_ra(resp_agent, source=self.src, res=url)
                    editor_name = re.search(r'(.*?)\s*\[.*?]', ed).group(1)
                    if "," in editor_name:
                        editor_name_splitted = re.split(r'\s*,\s*', editor_name)
                        firstName = editor_name_splitted[1]
                        lastName = editor_name_splitted[0]
                        if firstName.strip():
                            pub_ed.has_given_name(firstName)
                        pub_ed.has_family_name(lastName)
                    else:
                        pub_ed.has_name(editor_name)

            # lists of editor's IDs
            for identifier in ed_id_list:
                self.id_creator(pub_ed, identifier, ra=True)

            # editorRole
            AR = self.ar_index[self.row_meta]["editor"][ed_meta]
            ar_id = "ar/" + str(AR)
            url_ar = URIRef(self.url + ar_id)
            pub_ed_role = self.setgraph.add_ar(resp_agent, source=self.src, res=url_ar)

            if self.type == "proceedings article" and self.venue_graph:
                pub_ed_role.create_editor()
                self.venue_graph.has_contributor(pub_ed_role)
            elif (self.type == "book chapter" or self.type == "book part") and self.venue_graph:
                pub_ed_role.create_editor()
                self.venue_graph.has_contributor(pub_ed_role)
            else:
                pub_ed_role.create_editor()
                self.br_graph.has_contributor(pub_ed_role)

            pub_ed_role.is_held_by(pub_ed)
            edit_role_list.append(pub_ed_role)
            if len(edit_role_list) > 1:
                edit_role_list[edit_role_list.index(pub_ed_role)-1].has_next(pub_ed_role)

    def id_creator(self, graph, identifier, ra):

        new_id = None

        if ra:
            if identifier.startswith("crossref"):
                identifier = identifier.replace('crossref:', '')
                res = self.ra_index['crossref'][identifier]
                url = URIRef(self.url + "id/" + res)
                new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
                new_id.create_crossref(identifier)

            elif identifier.startswith("orcid"):
                identifier = identifier.replace("orcid:", "")
                res = self.ra_index['orcid'][identifier]
                url = URIRef(self.url + "id/" + res)
                new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
                new_id.create_orcid(identifier)

            elif identifier.startswith("viaf"):
                identifier = identifier.replace("viaf:", "")
                res = self.ra_index['viaf'][identifier]
                url = URIRef(self.url + "id/" + res)
                new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
                new_id.create_viaf(identifier)

            elif identifier.startswith("wikidata"):
                identifier = identifier.replace("wikidata:", "")
                res = self.ra_index['wikidata'][identifier]
                url = URIRef(self.url + "id/" + res)
                new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
                new_id.create_wikidata(identifier)

        elif identifier.startswith("doi"):
            identifier = identifier.replace("doi:", "")
            res = self.br_index['doi'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_doi(identifier)

        elif identifier.startswith("issn"):
            identifier = identifier.replace("issn:", "")
            res = self.br_index['issn'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_issn(identifier)

        elif identifier.startswith("isbn"):
            identifier = identifier.replace("isbn:", "")
            res = self.br_index['isbn'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_isbn(identifier)

        elif identifier.startswith("pmid"):
            identifier = identifier.replace("pmid:", "")
            res = self.br_index['pmid'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_pmid(identifier)

        elif identifier.startswith("pmcid"):
            identifier = identifier.replace("pmcid:", "")
            res = self.br_index['pmcid'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_pmcid(identifier)

        elif identifier.startswith("url"):
            identifier = identifier.replace("url:", "")
            res = self.br_index['url'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_url(identifier)

        elif identifier.startswith("wikidata"):
            identifier = identifier.replace("wikidata:", "")
            res = self.br_index['wikidata'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_wikidata(identifier)

        elif identifier.startswith("wikipedia"):
            identifier = identifier.replace("wikipedia:", "")
            res = self.br_index['wikipedia'][identifier]
            url = URIRef(self.url + "id/" + res)
            new_id = self.setgraph.add_id(resp_agent, source=self.src, res=url)
            new_id.create_wikipedia(identifier)

        if new_id:
            graph.has_identifier(new_id)
