# Converter test
_Tests are built using the builtin module of Python named `unittest`. Please, refer to [its documentation](https://docs.python.org/3.7/library/unittest.html)
in case of issues._

## run_process.py and run_process_citations.py
Tests for the Converter step are fully contained in this folder. They can be simply run with the following commands:
```bash
cd <path>/Converter
python -m unittest discover
```

If everything goes well, an 'OK' message is printed in the end.

## meta
Tests for the meta script are contained inside the [meta](../meta) folder.

There are two test modules, `tdd.curator_TDD` and `tdd.creator_TDD`.

### curator_TDD.py
This test module requires an active local triplestore endpoint to be running at the address `http://127.0.0.1:9999/blazegraph/sparql`.
Hence, [Blazegraph](https://github.com/blazegraph/database) should be used.

The `blazegraph.jar` file should be downloaded [from here](https://github.com/blazegraph/database/releases). A version equal
to 2.1.6 or superior is warmly suggested. An updated JAVA JRE must be installed on the machine.
```bash
cd <blazegraph_download_path>
java -jar ./blazegraph.jar
``` 

**Once started, the terminal window must not be closed, otherwise the triplestore will also be stopped!**

Now the test module can simply be run as follows:
```bash
cd <path>/Converter
python -m meta.tdd.curator_TDD
```

If everything goes well, an 'OK' message is printed in the end.

**The Blazegraph instance can now be safely stopped.**

### creator_TDD.py
The `creator_TDD.py` module can simply be run as follows:
```bash
cd <path>/Converter
python -m meta.tdd.creator_TDD
```

If everything goes well, an 'OK' message is printed in the end.
