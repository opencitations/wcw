# Enricher
The third step of the WCW workflow.

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
This module is the third part of the WCW workflow. It firstly tries to enrich the RDF chunk files produced by the Converter with additional external identifiers and, secondly, it deduplicates entities inside each chunk. 

It consists in a single script that wraps the functionalities offered by the `oc_graphenricher`
package. More information can be found in the [Github repository](https://github.com/opencitations/oc_graphenricher) and in the [online documentation](https://oc-graphenricher.readthedocs.io/en/latest/).

The enriched version of the input chunk file is stored in the `<path>/enricher_folder/enriched/` directory. The deduplicated version of the enriched chunk files is then stored in the `<path>/enricher_folder/deduplicated/`.

<!-- GETTING STARTED -->
## Getting Started
**A Python >=3.7 execution environment is required.** Please, install the dependencies listed
in the requirements.txt file by executing the following commands:
```bash
cd <path>/Enricher
pip install -r requirements.txt
```

It's not necessary to install anything. The user can simply download the Converter folder from this 
repository.

<!-- USAGE EXAMPLES -->
## Usage
The user should take care of creating a folder structure as follows:
```
'enricher_folder'--
                + 'enriched'--
                |           (initially empty)
                + 'deduplicated'--
                |               (initially empty)
```

### run_process.py
The configuration file of the script is available at this path: `Enricher/conf.py`.
| Constant | Description |
|---|---|
| `rdf_input_dir` | **the input RDF files folder. It should be `<path>/meta_folder/rdf_output/`.** |
| `rdf_output_dir` | **the output RDF files folder. It should be `<path>/enricher_folder/`.**
| `base_iri` | _a string that can be safely left as it is. It's a parameter needed by the oc_ocdm package._ |
| `resp_agent` | _a URI string representing the provenance agent which is considered responsible of the RDF graph manipulation (in this case of the modification/merge/deletion of new OCDM entities). It can be safely left as it is._ |
| `info_dir` | a support folder used by oc_ocdm. It should not be deleted until the end of the Enricher step and it should be the same for all the scripts of this workflow (it must be `<path>/meta_folder/info_dir/`).  |
| `supplier_prefix` | _a string that can be safely left empty. It's a parameter needed by the oc_ocdm package._ |

---

**Once configured**, the script can be simply run as follows:
```bash
cd <path>/Enricher
python run_process.py
```

<!-- LICENSE -->
## License
Distributed under the ISC License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contacts
|Project member |e-mail address |
|---|---|
| Silvio Peroni - [@essepuntato](https://twitter.com/essepuntato) | essepuntato@gmail.com |
| Marilena Daquino | marilena.daquino2@unibo.it |
| Giovanni Colavizza | giovannicolavizza@gmail.com |
| Gabriele Pisciotta | ga.pisciotta@gmail.com |
| Simone Persiani | iosonopersia@gmail.com |

Project Link: https://github.com/opencitations/wcw

## Acknowledgements
This project has been developed within the context of the ["Wikipedia Citations in Wikidata" grant](https://meta.wikimedia.org/wiki/Wikicite/grant/Wikipedia_Citations_in_Wikidata), 
under the supervision of prof. Silvio Peroni.
