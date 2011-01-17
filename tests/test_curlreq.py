import unittest
import os
import logging
from rdflib.Graph import Graph
from rdflib.Namespace import Namespace
from rdflib import URIRef, BNode, Literal
from FuXi.Rete.Util import generateTokenSet
from curate.rules import makeRuleStore

RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
HTTP = Namespace("http://www.w3.org/2006/http#")
CURL = Namespace("http://eris.okfn.org/ww/2010/12/curl#")

def fixture(filename):
    datadir = os.path.join(os.path.dirname(__file__), "data")
    return os.path.join(datadir, filename)
    
class TestCurlReq(unittest.TestCase):
    def setUp(self):
        ruleStore, ruleGraph, self.network = makeRuleStore([fixture("test_bad_url.n3")])

    def getreq(self, closureDelta, resource):
        """
        Utility function, equivalent roughly to

        SELECT ?req, ?resp WHERE {
            ?req http:requestURI %(resource)s .
            ?req http:resp ?resp
        } LIMIT 1
        """
        reqs = set(closureDelta.subjects(HTTP["requestURI"], resource))
        req = reqs.pop()
        resps = set(closureDelta.objects(req, HTTP["resp"]))
        resp = resps.pop()
        return req, resp
    
    def test_unresolvable_host(self):
        g = Graph()
        g.parse(fixture("cap-uk-payments-2009.rdf"))
        resource = URIRef("http://cap-payments.defra.../2008_All_CAP_Search_Results.xls")

        self.network.feedFactsToAdd(generateTokenSet(g))
        closureDelta = self.network.inferredFacts
        logging.debug("Inferred Triples:\n%s" % closureDelta.serialize(format="n3"))
        req, resp = self.getreq(closureDelta, resource)

        assert (resp, CURL["status"], CURL["Failure"]) in closureDelta
        assert (resp, HTTP["statusCodeNumber"], Literal("0")) in closureDelta

    def test_404(self):
        g = Graph()
        g.parse(fixture("dbpedia_broken.rdf"))
        resource = URIRef("http://eris.okfn.org/nonexistent")

        self.network.feedFactsToAdd(generateTokenSet(g))
        closureDelta = self.network.inferredFacts
        logging.debug("Inferred Triples:\n%s" % closureDelta.serialize(format="n3"))
        req, resp = self.getreq(closureDelta, resource)

        assert (resp, CURL["status"], CURL["Failure"]) in closureDelta
        assert (resp, HTTP["statusCodeNumber"], Literal("404")) in closureDelta
