# wcw
## Wikipedia Citations in Wikidata

This is the repository of the [Wikipedia Citations in Wikidata grant](https://meta.wikimedia.org/wiki/Wikicite/grant/Wikipedia_Citations_in_Wikidata).
It's a collection of scripts that can be used to extract citations from the English Wikipedia to 
external bibliographic resources, and then to upload them to Wikidata.

## Project description
Quoting the [grant's description](https://meta.wikimedia.org/wiki/Wikicite/grant/Wikipedia_Citations_in_Wikidata#Description):

> Our goal is to develop four software modules in Python (the codebase from now on) that can be
>    easily reused by developers in the Wikidata community:
>  1. [**extractor**](Extractor) a module to extract citation and bibliographic information from articles in
>    the English Wikipedia;
>  2. [**converter**](Converter) a module to convert extracted information into a CSV-based format compliant
>    with a shareable bibliographic data model, e.g., the OpenCitations Data Model;
>  3. [**enricher**](Enricher) a module for reconciling bibliographic resources and people (obtained in step 2)
>    with entities available in Wikidata via their persistent identifiers (primarily DOIs, 
>    QIDs, ORCIDs, VIAFs, then also persons, places and organisations if time allows);
>  4. [**pusher**](Pusher) a module to disambiguate, deduplicate, and load citation and bibliographic data
>    in Wikidata that reuses code already developed by the wikidata community as much as possible.

The repository folder structure reflects these same modules that constitue the entire workflow.

## Instructions
Each module has a `README` file that contains specific instructions on how to setup the execution
environment, on how to configure the modules and how to run them. Here, only a general overview of the 
entire process is given.

This particular workflow strictly requires that the user executes the given scripts in a particular
order:
  1. the [**Extractor**](Extractor) module takes as input a dump of the current English Wikipedia pages and outputs 
     a parquet dataset containing the extracted citations. Our suggestion is to directly download the
     [parquet dataset from here at Zenodo](https://zenodo.org/record/3940692#.X9JOIun0mL8) (the ZIP 
     file to be downloaded is called **"citations_from_wikipedia.zip"**).
  2. the [**Converter**](Converter) module takes as input the parquet dataset from the previous step and produces a 
     set of RDF files which are [OCDM compliant](https://figshare.com/articles/online_resource/Metadata_for_the_OpenCitations_Corpus/3443876).
  3. the [**Enricher**](Enricher) module takes as input the RDF files from the previous step and tries to enrich them
     as much as possible by adding external identifiers coming from various APIs. When the external
     identifiers are added, a deduplication step is applied to each RDF file.
  4. the [**Pusher**](Pusher) module take as input the enriched RDF files from the previous step and produces TSV
     files compliant with the QuickStatements input format that enable the user to bulk upload the
     citational data onto Wikidata.

More details can be found inside the `README` documents of each module; please refer to them for specific
information about the inner workings of each workflow step.

## License
Distributed under the ISC License. See `LICENSE` for more information.

## Contact
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
