import urllib2
from logging import getLogger

def httpGET(pats, pato):
    log = getLogger("httpGET(%s)" % pats.n3())
    log.debug("init")
    def f(s,_o):
        try:
            log.debug(s)
            fp = urllib2.urlopen(s)
            fp.read()
            fp.close()
            return True
        except Exception, e:
            log.warn("%s", e)
            return False
    return f
