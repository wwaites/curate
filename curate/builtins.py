import urllib2
from logging import getLogger

def httpGET(pats, pato):
    log = getLogger("httpGET(%s, %s)" % (pats.n3(), pato.n3()))
    log.debug("init")
    def f(_unused, resource):
        try:
            log.debug(resource)
            fp = urllib2.urlopen(resource)
            fp.read()
            fp.close()
            return True
        except Exception, e:
            log.warn("%s", e)
            return False
    return f
