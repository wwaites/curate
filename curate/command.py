import argparse

import warnings
warnings.simplefilter("ignore", DeprecationWarning)
import logging

from curate.rules import makeRuleStore
from rdflib.Graph import Graph
from FuXi.Rete.Util import generateTokenSet

def curate():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-b", dest="base", default="http://semantic.ckan.net/package/",
                        help="RDF description base")
    parser.add_argument("-r", dest="rules", action="append", default=[], help="N3 rules",)
    parser.add_argument("-v", dest="debug", action="store_true")
    parser.add_argument("datasets", nargs="*", help="Dataset(s) to check")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s[%(levelname)s]: %(message)s"
    )

    ruleStore, ruleGraph, network = makeRuleStore(args.rules)

    for dataset in args.datasets:
        network.reset()
        g = Graph()
        g.parse(args.base + dataset)
        network.feedFactsToAdd(generateTokenSet(g))
        print network.inferredFacts.serialize(format="n3")
