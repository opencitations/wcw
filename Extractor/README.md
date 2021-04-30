# Extractor
The first step of the [WCW workflow](..).

<summary><h2 style="display: inline-block">Table of Contents</h2></summary>
<ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#tests">Tests</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contacts">Contacts</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
</ol>

## About The Project
This module is the first part of the WCW workflow. Its aim is to extract citations from a full enwiki dump. It
stores them in a .parquet dataset which is also compressed with the [snappy algorithm by Google](https://opensource.google/projects/snappy).

The implementation and its related documentation can be found in the `Harshdeep1996/cite-classifications-wiki` Github repository.

We provide a copy of that repository inside the `Extractor/cite-classifications-wiki` subfolder: please, be aware that we
chose not to copy a couple of subfolders (because of their size!), as stated in the WARNING section of the `README.md` file
that can be found [here](cite-classifications-wiki).

## Tests
Tests (together with their instructions) can be found in the [test](test) subfolder.

## License
Distributed under the ISC License. See `LICENSE` for more information.

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
