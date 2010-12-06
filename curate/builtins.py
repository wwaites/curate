import urllib2
from logging import getLogger
from rdflib.Graph import ConjunctiveGraph
from rdflib import URIRef, Literal
from rdflib.store.SPARQL import SPARQLStore
from curate.work import queue

def httpGET(_unusedp, resourcep):
    """
    :param resourcep: resource pattern, the bound version of which
        checked

    Check if the given resource responds with data to an HTTP
    GET request.
    """
    log = getLogger("httpGET(%s, %s)" % (_unusedp.n3(), resourcep.n3()))
    log.debug("init")
    def f(_unused, resource):
        try:
            log.info(resource)
            fp = urllib2.urlopen(resource)
            fp.read()
            fp.close()
            return True
        except Exception, e:
            log.warn("%s", e)
            return False
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

def addTag(datasetp, tagp):
    def f(dataset, tag):
        queue.add(dataset, "tags", [unicode(tag)])
        return True
    return f

def addGroup(datasetp, groupp):
    def f(dataset, group):
        if isinstance(group, URIRef):
            _, group = group.rsplit("/", 1)
        elif isinstance(group, Literal):
            _, group = unicode(group)
        else:
            return False
        queue.add(dataset, "groups", [unicode(group)])
        return True
    return f
