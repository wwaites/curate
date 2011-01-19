import urllib2
from logging import getLogger
from rdflib.Graph import ConjunctiveGraph
from rdflib import URIRef, Literal
from rdflib.store.SPARQL import SPARQLStore
from curate.work import queue
from ll.url import URL

def cmpURI(lhsp, rhsp):
    """
    :param lhsp, rhsp: two urls to be compared according to
        RFC2396 equality
    """
    log = getLogger("cmpURI(%s, %s)" % (lhsp.n3(), rhsp.n3()))
    log.debug("init")
    def f(lhs, rhs):
        u1 = URL(lhs)
        u2 = URL(rhs)
        log.debug("%s == %s" % (u1, u2))
        return u1 == u2
    return f

def sparqlCheck(_unusedp, endpointp):
    """
    :param endpointp: endpoint pattern, the bound version of which
        will be checked

    Check if the SPARQL endpoint functions. In this context, to
    *function* means returning a result when given a simple query.
    The query used is:

        SELECT * WHERE { ?s ?p ?o } LIMIT 1
    """
    log = getLogger("sparqlCheck(%s, %s)" % (_unusedp.n3(), endpointp.n3()))
    log.debug("init")
    def f(_unused, endpoint):
        store = SPARQLStore(endpoint)
        log.info(endpoint)
        try:
            ## as generic a query as possible
            q = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
            for x in ConjunctiveGraph(store).query(q):
                return True
        except Exception, e:
            log.warn("%s", e)
        return False
    return f
