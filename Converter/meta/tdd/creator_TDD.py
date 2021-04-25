import unittest
from meta.scripts.creator import *
import csv
from rdflib.term import _toPythonMapping
from rdflib import XSD, compare, Graph
import os
import json


# The following function has been added for handling gYear and gYearMonth correctly.
# Source: https://github.com/opencitations/script/blob/master/ocdm/storer.py
# More info at https://github.com/RDFLib/rdflib/issues/806.

def hack_dates():
    if XSD.gYear in _toPythonMapping:
        _toPythonMapping.pop(XSD.gYear)
    if XSD.gYearMonth in _toPythonMapping:
        _toPythonMapping.pop(XSD.gYearMonth)


def open_csv(path):
    path = os.path.abspath(path)
    with open(path, 'r', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        data = [dict(csv_dict) for csv_dict in reader]
        return data


def open_json(path):
    path = os.path.abspath(path)
    with open(path) as json_file:
        data = json.load(json_file)
        return data


# creator executor
def prepare2test(name):
    data = open_csv("meta/tdd/testcases/testcase_data/testcase_" + name + "_data.csv")
    testcase_id_br = open_csv("meta/tdd/testcases/testcase_data/indices/" + name + "/index_id_br_" + name + ".csv")
    testcase_id_ra = open_csv("meta/tdd/testcases/testcase_data/indices/" + name + "/index_id_ra_" + name + ".csv")
    testcase_ar = open_csv("meta/tdd/testcases/testcase_data/indices/" + name + "/index_ar_" + name + ".csv")
    testcase_re = open_csv("meta/tdd/testcases/testcase_data/indices/" + name + "/index_re_" + name + ".csv")
    testcase_vi = open_json("meta/tdd/testcases/testcase_data/indices/" + name + "/index_vi_" + name + ".json")
    testcase_ttl = "meta/tdd/testcases/testcase_" + name + ".ttl"

    creator_info_dir = os.path.join("meta", "tdd", "creator_counter")
    creator = Creator(data, "https://w3id.org/oc/meta/", creator_info_dir, testcase_id_ra, testcase_id_br,
                      testcase_re, testcase_ar, testcase_vi)
    creator_setgraph = creator.creator()
    test_graph = Graph()
    hack_dates()
    test_graph = test_graph.parse(testcase_ttl, format="ttl")
    new_graph = Graph()
    for g in creator_setgraph.graphs():
        new_graph += g
    return test_graph, new_graph


class testcase_01(unittest.TestCase):
    def test(self):
        # testcase1: 2 different issues of the same venue (no volume)
        name = "01"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_02(unittest.TestCase):
    def test(self):
        # testcase2: 2 different volumes of the same venue (no issue)
        name = "02"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_03(unittest.TestCase):
    def test(self):
        # testcase3: 2 different issues of the same volume
        name = "03"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_04(unittest.TestCase):
    def test(self):
        # testcase4: 2 new IDS and different date format (yyyy-mm and yyyy-mm-dd)
        name = "04"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_05(unittest.TestCase):
    def test(self):
        # testcase5: NO ID scenario
        name = "05"
        test_graph, new_graph = prepare2test(name)

        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_06(unittest.TestCase):
    def test(self):
        # testcase6: ALL types test
        name = "06"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_07(unittest.TestCase):
    def test(self):
        # testcase7: all journal related types with an editor
        name = "07"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_08(unittest.TestCase):
    def test(self):
        # testcase8: all book related types with an editor
        name = "08"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_09(unittest.TestCase):
    def test(self):
        # testcase9: all proceeding related types with an editor
        name = "09"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


class testcase_10(unittest.TestCase):
    def test(self):
        # testcase10: a book inside a book series and a book inside a book set
        name = "10"
        test_graph, new_graph = prepare2test(name)
        self.assertEqual(compare.isomorphic(new_graph, test_graph), True)


def suite(testobj):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(testobj))
    return test_suite


'''
TestSuit = suite(testcase_01)

runner = unittest.TextTestRunner()
runner.run(TestSuit)
'''
x = 1
while x < 11:
    if x < 10:
        y = "0" + str(x)
    else:
        y = str(x)
    t = "testcase_" + y
    TestSuit = suite(eval(t))
    x += 1
    runner = unittest.TextTestRunner()
    runner.run(TestSuit)
