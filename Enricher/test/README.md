# Enricher test
_Tests are built using the builtin module of Python named `unittest`. Please, refer to [its documentation](https://docs.python.org/3.7/library/unittest.html)
in case of issues._

There are no specific tests for the Enricher step, which is simply a wrapper around the `oc_graphenricher` package.
The `oc_graphenricher` package itself is provided with tests that can be run by following these steps:
* the repository of the package should be downloaded from GitHub, for example with the following command
```bash
cd <path>
git clone https://github.com/opencitations/oc_graphenricher
```
* now move inside the package folder
```bash
cd ./oc_graphenricher
```
* finally, tests can be run
```bash
python -m unittest discover
```

If everything goes well, an 'OK' message is printed in the end.
