# Extractor test
_Tests are built using the builtin module of Python named `unittest`. Please, refer to [its documentation](https://docs.python.org/3.7/library/unittest.html)
in case of issues._

There are no specific tests for the Extractor step, which actually consists in simply executing the `cite-classifications-wiki`
scripts.
The `cite-classifications-wiki` project itself is provided with tests that can be run with the following commands:
```bash
cd <path>/Extractor/cite-classifications-wiki
python -m unittest discover
```

If everything goes well, an 'OK' message is printed in the end.
