# Pusher
The fourth and last step of the WCW workflow.

<!-- TABLE OF CONTENTS -->
<summary><h2 style="display: inline-block">Table of Contents</h2></summary>
<ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
</ol>

<!-- ABOUT THE PROJECT -->
## About The Project
This module is the fourth and last part of the WCW workflow. It aims at producing TSV files (compliant with QuickStatements) that can be manually bulk-uploaded onto Wikidata. It takes
as input RDF files produced by the Converter and eventually processed by the Enricher. During
the execution, OCDM entities from the input graphs are reconciled with Wikidata entities. The
reconciliation is mainly based on the external identifiers associated with each bibliographic
entity, author, publisher, etc... The entities that cannot be reconciled are created from scratch using the related information stored in the input RDF files.

In order to fully execute the Pusher step of the workflow, the user must launch two scripts in the
following mandatory order:
  1. the **run_process.py** script: it processes the "bibliographic" RDF chunk files that may come from the Enricher or directly from the Converter. It's an interactive script that repeatedly overwrites a TSV file with new statements and then pauses (waiting for the user to manually bulk-upload them).
  2. the **run_process_citations.py** script: processes the "citations" RDF chunk files that come from the Converter (they're not involved in the Enricher step). It's not an interactive script: it produces a TSV file that should be manually bulk-uploaded only at the end of its execution.

<!-- GETTING STARTED -->
## Getting Started
**A Python >=3.7 execution environment is required.** Please, install the dependencies listed
in the requirements.txt file by executing the following commands:
```bash
cd <path>/Pusher
pip install -r requirements.txt
```

It's not necessary to install anything. The user can simply download the Converter folder from this 
repository.

<!-- USAGE EXAMPLES -->
## Usage
The user should take care of creating a folder structure as follows:
```
'pusher_folder'--
                + 'citations_mapping.csv' (empty file)
                + 'citations_batch.tsv' (empty file)
                + 'temp_TSV_batch.tsv' (empty file)
```

The configuration file of **both scripts** is available at this path: `Pusher/config.py`.
| Constant | Description |
|---|---|
| `base_iri` | _a string that should be left as it is. It's a parameter needed by the oc_ocdm package._ |
| `query_timeout` | the timeout duration (integer value in seconds) for each SPARQL query made against the Wikidata endpoint. (See the `reconciliator.py` module). |
| `query_wait_time` | the time to wait before each new SPARQL query (integer value in seconds). This is useful in order to avoid errors due to the limited amount of queries that can be performed in a minute against the Wikidata endpoint. (See the `reconciliator.py` module). |
| `resp_agent` | _an URI string representing the provenance agent which is considered responsible of the RDF graph manipulation (in this case of the creation of new OCDM entities). It can be left as it is, since provenance isn't particularly interesting for this workflow._ |
| `base_dir` | **the input RDF files folder.** It could be `<path>/enricher_folder/deduplicated/` (for enriched and deduplicated RDF graphs), `<path>/enricher_folder/enriched/` (for enriched-only RDF graphs) or `<path>/meta_folder/rdf_output/` (for RDF graphs produced by the Converter and not processed by the Enricher). |
| `pusher_citations_csv_file` | **the path of a temporary CSV file used by `run_process_citations.py`. It should be `<path>/pusher_folder/citations_mapping.csv`.** |
| `pusher_citations_batch_file` | **the output path of the `run_process_citations.py` script.** It's a TSV file (initially empty) to which the script appends the TSV statements to be bulk-uploaded via the web interface of QuickStatements. It should be `<path>/pusher_folder/citations_batch.tsv`. |
| `citations_batches_dir` | **the input RDF files folder for the `run_process_citations.py` script.** It should be `<path>/citations_folder/rdf_output/` (the same as `converter_citations_rdf_output_dir` in `Converter/conf/conf_citations.py`). |
| `temp_TSV_batch_output_file` | **the output path of the `run_process.py` script.** It's a TSV file that gets overwritten several times by the script: every time the file is overwritten with new TSV statements, the script pauses and waits for the user to bulk-upload them via the web interface of QuickStatements. It should be `<path>/pusher_folder/temp_TSV_batch.tsv`. |

### run_process.py
**Once configured**, the script can be simply run as follows:
```bash
cd <path>/Pusher
python run_process.py
```

### run_process_citations.py
**Once configured**, the script can be simply run as follows:
```bash
cd <path>/Pusher
python run_process_citations.py
```

<!-- LICENSE -->
## License
Distributed under the ISC License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact
Silvio Peroni - [@essepuntato](https://twitter.com/essepuntato) - essepuntato@gmail.com

Project Link: https://github.com/opencitations/wcw

## Acknowledgements
This project has been developed within the context of the ["Wikipedia Citations in Wikidata" grant](https://meta.wikimedia.org/wiki/Wikicite/grant/Wikipedia_Citations_in_Wikidata), 
under the supervision of prof. Silvio Peroni.
