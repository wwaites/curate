import unittest
import os
import logging
from rdflib.Graph import Graph
from rdflib.Namespace import Namespace
from rdflib import URIRef, BNode, Literal
from FuXi.Rete.Util import generateTokenSet
from curate.rules import makeRuleStore
from StringIO import StringIO

RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

def fixture(filename):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    return os.path.join(datadir, filename)
    
class TestRegexp(unittest.TestCase):
    def setUp(self):
        ruleStore, ruleGraph, self.network = makeRuleStore([fixture("test_regexp.n3")])
        g = Graph()
        g.parse(StringIO("""
        @prefix dc: <http://purl.org/dc/terms/>.
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        
        <http://example.org/> dc:title "abc/123" .
        <http://example.org/> rdfs:seeAlso <http://example.org/12345.txt>.
        """), format="n3")
        self.network.feedFactsToAdd(generateTokenSet(g))
        logging.debug("Inferred Facts:\n%s" % self.network.inferredFacts.serialize(format="n3"))
        
    def test_regexp(self):
        closureDelta = self.network.inferredFacts

        expected = [
            (Literal("invalid[+"), RDFS["comment"], Literal("unexpected end of regular expression")),
            ]

        for statement in expected:
            assert statement in closureDelta, "%s not found in inferred triples" % expected

        q = """
        PREFIX dc: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX curate: <http://eris.okfn.org/ww/2010/12/curate#>

        SELECT ?right
        WHERE {
            ?x curate:match ?m .
            ?m curate:name "right" .
            ?m curate:value ?right
        }
        """
        assert u"123" in closureDelta.query(q)

        q = """
        PREFIX dc: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX curate: <http://eris.okfn.org/ww/2010/12/curate#>

        SELECT ?ident
        WHERE {
            ?x curate:match ?m .
            ?m curate:name "ident" .
            ?m curate:value ?ident
        }
        """
        assert u"12345" in closureDelta.query(q)
