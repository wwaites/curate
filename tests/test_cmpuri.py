import unittest
import os
import logging
from rdflib.Graph import Graph
from rdflib.Namespace import Namespace
from rdflib import URIRef, BNode, Literal
from FuXi.Rete.Util import generateTokenSet
from curate.rules import makeRuleStore
from StringIO import StringIO

OWL = Namespace("http://www.w3.org/2002/07/owl#")

def fixture(filename):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    return os.path.join(datadir, filename)
    
class TestUriCmp(unittest.TestCase):
    def setUp(self):
        ruleStore, ruleGraph, self.network = makeRuleStore([fixture("test_cmpuri.n3")])
        g = Graph()
        g.parse(StringIO("""
        <http://example.org/> a _:x .
        <http://EXAMPLE.ORG/> a _:x .
        <HTTP://example.org:80/> a _:x .
        """), format="n3")
        self.network.feedFactsToAdd(generateTokenSet(g))

    def test_uricmp(self):
    
        print self.network.inferredFacts.serialize(format="n3")
