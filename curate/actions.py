import urllib2
from urlparse import urlparse
from datetime import datetime
from logging import getLogger
from rdflib.Graph import ConjunctiveGraph, Graph
from rdflib import URIRef, Literal, Variable, BNode
from rdflib.Namespace import Namespace
from rdflib.store.SPARQL import SPARQLStore
from FuXi.Rete.Util import generateTokenSet
from curate.work import queue

RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
DCT = Namespace("http://purl.org/dc/terms/")
HTTP = Namespace("http://www.w3.org/2006/http#")
METH = Namespace("http://www.w3.org/2008/http-methods#")

class Action(object):
    def __init__(self, sbind, obind):
        self.sbind = sbind
        self.obind = obind
        self.log = getLogger("%s(%s, %s)" % (self.__class__.__name__, sbind.n3(), obind.n3()))
        self.log.debug("init")
    def get(self, term, token):
        if isinstance(term, Variable):
            for binding in token.bindings:
                if term in binding:
                    return binding[term]
        return term

class httpReq(Action):
    def __call__(self, tNode, inferredTriple, token, _binding, debug = False):
        """
        Check if the given resource responds with data to an HTTP
        REQ request.
        """
        resource = self.get(self.sbind, token)
        method = self.get(self.obind, token)
        self.log.info("%s" % resource) 

        class _Request(urllib2.Request):
            def get_method(self):
                return method
        request = _Request(resource)

        #g = tNode.network.inferredFacts
        g = Graph()
        conn = BNode()
        g.add((conn, RDF["type"], HTTP["Connection"]))
        g.add((conn, DCT["date"], Literal(datetime.utcnow())))
        parsed = urlparse(resource)
        host, port = parsed.hostname, parsed.port
        if port is None:
            if parsed.scheme == "https:":
                port = 443
            else:
                port = 80
        g.add((conn, HTTP["connectionAuthority"], Literal("%s:%s" % (host, port))))

        req = BNode()
        g.add((conn, HTTP["requests"], req))
        g.add((req, RDF["type"], HTTP["Request"]))
        g.add((req, HTTP["methodName"], Literal("HEAD")))
        g.add((req, HTTP["mthd"], METH["HEAD"]))
        g.add((req, HTTP["requestURI"], resource))
        if request.headers:
            self.record_headers(g, req, request.headers)

        resp = BNode()
        g.add((req, HTTP["resp"], resp))
        g.add((resp, RDF["type"], HTTP["Response"]))
        
        try:
            response = urllib2.urlopen(request)
            g.add((resp, HTTP["statusCodeNumber"], Literal("%s" % response.getcode())))
            if response.headers:
                self.record_headers(g, resp, response.headers)
            content = response.read(4096)
            response.close()
        except urllib2.HTTPError, response:
            g.add((resp, HTTP["statusCodeNumber"], Literal("%s" % response.getcode())))
            if response.headers:
                self.record_headers(g, resp, response.headers)
            content = response.read(4096)
            response.close()
            self.log.error("%s %s" % (resource, response))
        except urllib2.URLError, e:
            g.add((resp, HTTP["statusCodeNumber"], Literal("-1")))
            g.add((conn, RDFS["comment"], Literal(e.reason)))
            self.log.error("%s %s" % (resource, e))

        tNode.network.feedFactsToAdd(generateTokenSet(g))
        tNode.network.inferredFacts += g

    def record_headers(self, g, msg, hdict):
        for h in hdict:
            head = BNode()
            g.add((msg, HTTP["headers"], head))
            g.add((head, RDF["type"], HTTP["MessageHeader"]))
            g.add((head, HTTP["fieldName"], Literal(h)))
            g.add((head, HTTP["fieldValue"], Literal(hdict[h])))

class addTag(Action):
    def __call__(self, tNode, inferredTriple, token, _binding, debug = False):
        dataset = self.get(self.sbind, token)
        tag = self.get(self.obind, token)
        queue.add(dataset, "tags", [unicode(tag)])

class delTag(Action):
    def __call__(self, tNode, inferredTriple, token, _binding, debug = False):
        dataset = self.get(self.sbind, token)
        tag = self.get(self.obind, token)
        queue.remove(dataset, "tags", [unicode(tag)])

class addGroup(Action):
    def __call__(self, tNode, inferredTriple, token, _binding, debug = False):
        dataset = self.get(self.sbind, token)
        group = self.get(self.obind, token)

        if isinstance(group, URIRef):
            _, group = group.rsplit("/", 1)
        elif isinstance(group, Literal):
            _, group = unicode(group)
        else:
            return
        queue.add(dataset, "groups", [unicode(group)])
