import json
import html
from bs4 import BeautifulSoup
from meta.lib.id_manager.orcidmanager import ORCIDManager
from meta.lib.csvmanager import CSVManager
from meta.lib.id_manager.issnmanager import ISSNManager
from meta.lib.id_manager.isbnmanager import ISBNManager
from meta.lib.id_manager.doimanager import DOIManager


class crossrefProcessing:

    def __init__(self, orcid_index, doi_csv=None):
        if doi_csv:
            self.doi_set = CSVManager.load_csv_column_as_set(doi_csv, "doi")
        else:
            self.doi_set = None
        self.orcid_index = CSVManager(orcid_index)
        self.data = list()

    def csv_creator(self, raw_data_path):
        with open(raw_data_path, encoding="utf-8") as json_file:

            raw_data = json.load(json_file)
            # input_data = raw_data["items"]

            for x in raw_data:
                if "DOI" in x:
                    if isinstance(x["DOI"], list):
                        doi = DOIManager().normalise(str(x["DOI"][0]))
                    else:
                        doi = DOIManager().normalise(str(x["DOI"]))
                if (doi and self.doi_set and doi in self.doi_set) or (doi and not self.doi_set):
                    row = dict()

                    # create empty row
                    keys = ["id", "title", "author", "pub_date", "venue", "volume", "issue", "page", "type",
                            "publisher", "editor"]
                    for k in keys:
                        row[k] = ""

                    if "type" in x:
                        row["type"] = x["type"].replace("-", " ")

                    # row["id"]
                    idlist = list()
                    idlist.append(str("doi:" + doi))

                    if "ISBN" in x:
                        if row["type"] in {"book", "monograph", "edited book"}:
                            if isinstance(x["ISBN"], list):
                                for i in x["ISBN"]:
                                    self.issn_worker(str(i), idlist)
                            else:
                                isbnid = str(x["ISBN"])
                                self.isbn_worker(isbnid, idlist)

                    if "ISSN" in x:
                        if row["type"] in {"journal", "series", "report series", "standard series"}:
                            if isinstance(x["ISSN"], list):
                                for i in x["ISSN"]:
                                    self.issn_worker(str(i), idlist)
                            else:
                                issnid = str(x["ISSN"])
                                self.issn_worker(issnid, idlist)
                    row["id"] = " ".join(idlist)

                    # row["title"]
                    if "title" in x:
                        if x["title"]:
                            if isinstance(x["title"], list):
                                text_title = x["title"][0]
                            else:
                                text_title = x["title"]

                            soup = BeautifulSoup(text_title, "html.parser")
                            row["title"] = soup.get_text().replace("\n", "")

                    # row["author"]
                    if "author" in x:
                        dict_orcid = None
                        if doi and not all("ORCID" in at for at in x["author"]):
                            dict_orcid = self.orcid_finder(doi)
                        autlist = list()
                        for at in x["author"]:
                            if "family" in at:
                                f_name = at["family"]
                                g_name = at["given"]
                                if "given" in at:
                                    aut = f_name + ", " + g_name
                                else:
                                    aut = f_name + ", "
                                orcid = None
                                if "ORCID" in at:
                                    if isinstance(at["ORCID"], list):
                                        orcid = str(at["ORCID"][0])
                                    else:
                                        orcid = str(at["ORCID"])
                                    if ORCIDManager().is_valid(orcid):
                                        orcid = ORCIDManager().normalise(orcid)
                                    else:
                                        orcid = None
                                elif dict_orcid:
                                    for ori in dict_orcid:
                                        orc_n = dict_orcid[ori].split(", ")
                                        orc_f = orc_n[0]
                                        orc_g = orc_n[1]
                                        if f_name.lower() in orc_f.lower() or orc_f.lower() in f_name.lower():
                                            # and (g_name.lower() in orc_g.lower() or orc_g.lower() in g_name.lower()):
                                            orcid = ori
                                if orcid:
                                    aut = aut + " [" + "orcid:" + str(orcid) + "]"
                                autlist.append(aut)

                        row["author"] = "; ".join(autlist)

                    # row["date"]
                    if "issued" in x:
                        row["pub_date"] = "-".join([str(y) for y in x["issued"]["date-parts"][0]])

                    # row["venue"]
                    if "container-title" in x:
                        if isinstance(x["container-title"], list):
                            ventit = str(x["container-title"][0]).replace("\n", "")
                        else:
                            ventit = str(x["container-title"]).replace("\n", "")
                        ven_soup = BeautifulSoup(ventit, "html.parser")
                        ventit = html.unescape(ven_soup.get_text())
                        venidlist = list()
                        if "ISBN" in x:
                            if row["type"] in {"book chapter", "book part"}:
                                if isinstance(x["ISBN"], list):
                                    for i in x["ISBN"]:
                                        self.issn_worker(str(i), venidlist)
                                else:
                                    venisbnid = str(x["ISBN"])
                                    self.isbn_worker(venisbnid, venidlist)

                        if "ISSN" in x:
                            if row["type"] in {"journal article", "journal volume", "journal issue"}:
                                if isinstance(x["ISSN"], list):
                                    for i in x["ISSN"]:
                                        self.issn_worker(str(i), venidlist)
                                else:
                                    venissnid = str(x["ISSN"])
                                    self.issn_worker(venissnid, venidlist)
                        if venidlist:
                            row["venue"] = ventit + " [" + " ".join(venidlist) + "]"
                        else:
                            row["venue"] = ventit

                    if "volume" in x:
                        row["volume"] = x["volume"]
                    if "issue" in x:
                        row["issue"] = x["issue"]
                    if "page" in x:
                        row["page"] = x["page"]

                    if "publisher" in x:
                        if "member" in x:
                            row["publisher"] = x["publisher"] + " [" + "crossref:" + x["member"] + "]"
                        else:
                            row["publisher"] = x["publisher"]

                    if "editor" in x:
                        editlist = list()
                        for ed in x["editor"]:
                            if "family" in ed:
                                if "given" in ed:
                                    edit = ed["family"] + ", " + ed["given"]
                                else:
                                    edit = ed["family"] + ", "
                                edorcid = None
                                if "ORCID" in ed:
                                    if isinstance(ed["ORCID"], list):
                                        edorcid = str(ed["ORCID"][0])
                                    else:
                                        edorcid = str(ed["ORCID"])
                                    if ORCIDManager().is_valid(edorcid):
                                        edorcid = ORCIDManager().normalise(edorcid)
                                    else:
                                        edorcid = None
                                    if edorcid:
                                        edit = edit + " [orcid:" + str(edorcid) + "]"
                                editlist.append(edit)
                        row["editor"] = "; ".join(editlist)
                    self.data.append(row)
        return self.data

    def orcid_finder(self, doi):
        found = dict()
        doi = doi.lower()
        orcids = self.orcid_index.get_value(doi)
        if orcids:
            for orc in orcids:
                orc = orc.replace("]", "").split(" [")
                found[orc[1]] = orc[0].lower()
        return found

    @staticmethod
    def issn_worker(issnid, idlist):
        if ISSNManager().is_valid(issnid):
            issnid = ISSNManager().normalise(issnid)
            idlist.append(str("issn:" + issnid))

    @staticmethod
    def isbn_worker(isbnid, idlist):
        if ISBNManager().is_valid(isbnid):
            isbnid = ISBNManager().normalise(isbnid)
            idlist.append(str("isbn:" + isbnid))
