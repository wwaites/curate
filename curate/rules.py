import pkg_resources
from rdflib.Graph import Graph
from rdflib import URIRef
from rdflib import Namespace
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Horn.HornRules import HornFromN3

CURATE = Namespace("http://eris.okfn.org/ww/2010/12/curate#")

import logging

def makeRuleStore(rules):
    log = logging.getLogger("makeRuleStore")
    builtins = {}
    for ep in pkg_resources.iter_entry_points("curate.builtins"):
        log.info("Adding builtin curate:%s" % ep.name)
        builtin = ep.load()
        builtins[CURATE[ep.name]] = builtin

    ruleStore, ruleGraph, network = SetupRuleStore(makeNetwork=True,additionalBuiltins=builtins)

    for ruleFile in rules:
        log.info("Adding ruleset %s" % ruleFile)
        for rule in HornFromN3(ruleFile):
            network.buildNetworkFromClause(rule)

    return ruleStore, ruleGraph, network

