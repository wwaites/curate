import pkg_resources
from rdflib.Graph import Graph
from rdflib import URIRef
from rdflib import Namespace
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Horn.HornRules import HornFromN3
from FuXi.Horn.PositiveConditions import Uniterm

CURATE = Namespace("http://eris.okfn.org/ww/2010/12/curate#")

import logging
log = logging.getLogger(__name__)

def getBuiltins():
    builtins = {}
    for ep in pkg_resources.iter_entry_points("curate.builtins"):
        log.info("Adding builtin curate:%s" % ep.name)
        builtin = ep.load()
        builtins[CURATE[ep.name]] = builtin
    return builtins

def getActions():
    actions = {}
    for ep in pkg_resources.iter_entry_points("curate.actions"):
        log.info("Adding action curate:%s" % ep.name)
        action = ep.load()
        actions[CURATE[ep.name]] = action
    return actions

def makeRuleStore(rules):
    builtins = getBuiltins()
    ruleStore, ruleGraph, network = SetupRuleStore(makeNetwork=True,
                                                   additionalBuiltins=builtins)

    for ruleFile in rules:
        log.info("Adding ruleset %s" % ruleFile)
        for rule in HornFromN3(ruleFile):
            network.buildNetworkFromClause(rule)

    actions = getActions()
    for tNode in network.terminalNodes:
        for rule in tNode.rules:
            if not isinstance(rule.formula.head, Uniterm):
                continue
            headTriple = rule.formula.head.toRDFTuple()
            for pred in actions:
                if headTriple[1] == pred:
                    action = actions[pred](headTriple[0], headTriple[2])
                    tNode.executeActions[headTriple] = (True, action)

    return ruleStore, ruleGraph, network
