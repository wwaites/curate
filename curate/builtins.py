import urllib2
from logging import getLogger
from rdflib.Graph import ConjunctiveGraph
from rdflib.store.SPARQL import SPARQLStore

def httpGET(pats, pato):
    log = getLogger("httpGET(%s, %s)" % (pats.n3(), pato.n3()))
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

def sparqlCheck(pats, pato):
    log = getLogger("sparqlCheck(%s, %s)" % (pats.n3(), pato.n3()))
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
