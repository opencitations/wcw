from meta.crossref.crossrefProcessing import *
import os
import csv
from argparse import ArgumentParser


def preprocess(crossref_json_dir, orcid_doi_filepath, csv_dir, wanted_doi_filepath=None):
    for filename in os.listdir(crossref_json_dir):
        if filename.endswith(".json"):
            json_file = os.path.join(crossref_json_dir, filename)
            crossref_csv = crossrefProcessing(orcid_doi_filepath, wanted_doi_filepath)
            new_filename = filename.replace(".json", ".csv")
            filepath = os.path.join(csv_dir, new_filename)
            pathoo(filepath)
            data = crossref_csv.csv_creator(json_file)
            with open(filepath, 'w', newline='', encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, data[0].keys(), delimiter=',', quotechar='"',
                                             quoting=csv.QUOTE_NONNUMERIC)
                dict_writer.writeheader()
                dict_writer.writerows(data)


def pathoo(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


if __name__ == "__main__":
    arg_parser = ArgumentParser("run_preprocess.py", description="This script create csv files from Crossref json,"
                                                                 " enriching them thanks to an doi-orcid index")

    arg_parser.add_argument("-c", "--crossref", dest="crossref_json_dir", required=True,
                            help="Crossref json files directory")
    arg_parser.add_argument("-o", "--orcid", dest="orcid_doi_filepath", required=True,
                            help="Orcid-doi index filepath, to enrich data")
    arg_parser.add_argument("-v", "--csv", dest="csv_dir", required=True,
                            help="Directory where CSV will be stored")
    arg_parser.add_argument("-w", "--wanted", dest="wanted_doi_filepath", required=False,
                            help="A CSV filepath containing what DOI to process, not mandatory")

    args = arg_parser.parse_args()

    preprocess(args.crossref_json_dir, args.orcid_doi_filepath, args.csv_dir, args.wanted_doi_filepath)
