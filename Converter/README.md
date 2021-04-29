# Converter
The second step of the WCW workflow.

<!-- TABLE OF CONTENTS -->
<summary><h2 style="display: inline-block">Table of Contents</h2></summary>
<ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contacts">Contacts</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
</ol>

<!-- ABOUT THE PROJECT -->
## About The Project
This module is the second part of the WCW workflow. It aims at converting citational data stored in a parquet
dataset into [OCDM compliant](https://figshare.com/articles/online_resource/Metadata_for_the_OpenCitations_Corpus/3443876) RDF graphs. The OpenCitations DataModel is used as an intermediate data model which is capable of
storing bibliographic entities such as journal articles, books, authors, publishers, scientific journals
and more.

In order to fully execute the Converter step of the workflow, the user must launch three scripts in the
following mandatory order:
  1. the **run_process.py** script: it converts the input parquet dataset into a folder full of CSV
     files that are compliant with a particular OpenCitations tool called [meta](https://github.com/opencitations/meta).
  2. the **meta** script: it's an OpenCitations tool that is able to produce [OCDM compliant](https://figshare.com/articles/online_resource/Metadata_for_the_OpenCitations_Corpus/3443876) RDF files 
     starting from properly structured CSV files. It's used to generate RDF files containing the 
     bibliographic entities involved in the citations between English Wikipedia pages and external
     resources, but it doesn't contain the Citation entities which should describe the relations between them.
  3. the **run_process_citations.py** script: it reads from a particular subfolder in which the 
     **run_process.py** script exports CSV files containing citations and also from the CSV output files
     of **meta**. Its goal is to produce additional RDF files containing Citation entities that
     describe relations between citing entities and cited ones.

For the correct execution of the second and third step, a running instance of an initially empty 
triplestore is needed. We suggest to use Blazegraph version >=2.1.6 (which is the one we used to
test and development). The 'blazegraph.jar' file can be downloaded [from here](https://github.com/blazegraph/database/releases) (it requires an updated Java Runtime Environment).

<!-- GETTING STARTED -->
## Getting Started
**A Python >=3.7 execution environment is required.** Please, install the dependencies listed
in the requirements.txt file by executing the following commands:
```bash
cd <path>/Converter
pip install -r requirements.txt
```

It's not necessary to install anything. The user can simply download the Converter folder from this 
repository.

A new and clean instance of a triplestore is required by the **meta** and **run_process_citations.py** scripts. It should be kept alive during their entire execution.

<!-- USAGE EXAMPLES -->
## Usage
### run_process.py
The configuration file of this script is available at this path: `Converter/conf/conf.py`.
| Constant | Description |
|---|---|
| `parquet_engine` | the engine to be used when extracting data from the initial parquet dataset. Both `pyarrow`and `fastparquet` are supported by the `pandas` function `read_parquet` ([documentation here](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html)). Since the given dataset is compressed, the user should also install `python-snappy` in the same Python environment. The suggested choice is `pyarrow`. |
| `process_pool_size` | an integer representing the number of simultaneous processes that should be spawned by the script. A value of 0 or less is automatically replaced by the number of logical CPU threads of the system. For a sequential execution (which, by the way, is discouraged by the author), a value of 1 could be used. |
| `classify_even_if_type_is_uncertain` | a bool flag. Some citations do not have any ID that can help us classifying them (i.e. doi, pmid, isbn, ...). Should the script try to label them based on the 'type_of_citation' column? (See module `classifier.py`). |
| `input_parquet_file` | **the path of the parquet dataset (it's supposed to be a folder named `dataset.parquet`).** |
| `extracted_csv_dir` | **the output folder of this script.** |
| `allowed_citation_types` | a set of strings representing the allowed types of citations. When importing data from the parquet dataset, rows with a 'type_of_citation' (Wikipedia citation template) different from any of them will be discarded. (See module `reader.py`). **Default values SHOULD be kept (the script was written with them in mind).** |

**Once configured**, the script can be simply run as follows:
```bash
cd <path>/Converter
python run_process.py
```

### meta
`meta` is an OpenCitations tool available at [this Github repository](https://github.com/opencitations/meta).
A copy of the code is made available in this repository, inside the same `Converter` folder: the provided version is guaranteed to work well with the rest of the WCW scripts.

The user should take care of creating a folder structure as follows:
```
'meta_folder'--
              + 'csv_output'--
              |             (initially empty)
              + 'index'--
              |        (initially empty)
              + 'info_dir'--
              |           (initially empty)
              + 'rdf_output'--
              |             (initially empty)
              + 'auxiliary.txt' (empty file)
```

The configuration file of this project is available at this path: `Converter/meta/lib/conf.py`.
| Constant | Description |
|---|---|
| `base_dir` | **the RDF files output folder. It should be `<path>/meta_folder/rdf_output/`.** |
| `base_iri` | _a string that should be left as it is. It's a parameter needed by the oc_ocdm package._ |
| `triplestore_url` | **the SPARQL endpoint of the active triplestore. It must be a URL.** |
| `context_path` | _a string that should be left as it is. It's a parameter needed by the oc_ocdm package._ |
| `info_dir` | **the path of a temporary folder needed by the oc_ocdm package. It should be `<path>/meta_folder/info_dir/`.** |
| `dir_split_number` | _an integer value that should be left as it is. It's a parameter needed by the oc_ocdm package._ |
| `items_per_file` | _an integer value that should be left as it is. It's a parameter needed by the oc_ocdm package._ |
| `default_dir` | _a string that should be left as it is. It's a parameter needed by the oc_ocdm package._ |
| `supplier_prefix` | _a string that can be safely left empty. It's a parameter needed by the oc_ocdm package._ |
| `resp_agent` | _an URI string representing the provenance agent which is considered responsible of the RDF graph manipulation (in this case of the creation of new OCDM entities). It can be left as it is, since provenance isn't particularly interesting for this workflow._ |
| `rdf_output_in_chunks` | **a bool flag. For the WCW workflow, it MUST be valued as `True`.** |

**Once configured**, the script can be simply run as follows:
```bash
cd <path>/Converter
python -m meta.run_process -c "<PATH_1>" -v "<PATH_2>" -i "<PATH_3>" -a "<PATH_4>" -s "https://zenodo.org/record/3940692#.YGhw6s9xfcs"
```
, where:
  * <PATH_1> = the `run_process.py` CSV output dir (it MUST be the same as `extracted_csv_dir` from `Converter/conf/conf.py`);
  * <PATH_2> = the `meta` CSV output dir (`<path>/meta_folder/csv_output/`);
  * <PATH_3> = a `meta` temporary folder (`<path>/meta_folder/index`);
  * <PATH_4> = the `meta` auxiliary file (`<path>/meta_folder/auxiliary.txt`).

### run_process_citations.py
The user should take care of creating a folder structure as follows:
```
'citations_folder'--
                   + 'csv_output'--
                   |             (initially empty)
                   + 'info_dir'--
                   |           (initially empty)
                   + 'rdf_output'--
                                 (initially empty)
```

The configuration file of this script is available at this path: `Converter/conf/conf_citations.py`.
**The user should change only variables which are listed down below: other values should be kept unchanged, since they are default values for parameters that are needed by the oc_ocdm package.**

| Constant | Description |
|---|---|
| `meta_csv_output_dir` | the CSV files output directory of `meta` (it should be `<path>/meta_folder/csv_output/`). |
| `citations_csv_dir` | CSV files input directory (it should be `extracted_csv_dir`+"/citations/", with `extracted_csv_dir` value taken from the `Converter/conf/conf.py` file). |
| `converter_citations_info_dir` | a temporary folder (it should be `<path>/citations_folder/info_dir/`). |
| `converter_citations_csv_output_dir` | CSV files output directory (it should be `<path>/citations_folder/csv_output/`). |
| `converter_citations_rdf_output_dir` | RDF files output directory (it should be `<path>/citations_folder/rdf_output/`). |
| `triplestore_url` | it should be the same as `triplestore_url` from `Converter/meta/lib/conf.py`. |
| `info_dir` | it should be the same string as `info_dir` from `Converter/meta/lib/conf.py`. |
| `supplier_prefix` | _a string that can be safely left empty. It's a parameter needed by the oc_ocdm package._ |
| `rdf_output_in_chunks` | **this bool flag MUST be valued as `True`.** |

**Once configured**, the script can be simply run as follows:
```bash
cd <path>/Converter
python run_process_citations.py
```

<!-- LICENSE -->
## License
Distributed under the ISC License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contacts
|Project member |e-mail address |
|---|---|
| Gabriele Pisciotta | ga.pisciotta@gmail.com |
| Giovanni Colavizza | giovannicolavizza@gmail.com |
| Marilena Daquino | marilena.daquino2@unibo.it |
| Silvio Peroni - [@essepuntato](https://twitter.com/essepuntato) | essepuntato@gmail.com |
| Simone Persiani | iosonopersia@gmail.com |

Project Link: https://github.com/opencitations/wcw

## Acknowledgements
This project has been developed within the context of the ["Wikipedia Citations in Wikidata" grant](https://meta.wikimedia.org/wiki/Wikicite/grant/Wikipedia_Citations_in_Wikidata), 
under the supervision of prof. Silvio Peroni.
