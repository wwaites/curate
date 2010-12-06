import argparse

import warnings
warnings.simplefilter("ignore", DeprecationWarning)
import logging

from curate.rules import makeRuleStore
from rdflib.Graph import Graph
from FuXi.Rete.Util import generateTokenSet
from curate.work import queue

def curate():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-b", dest="base", default="http://semantic.ckan.net/package/",
                        help="RDF description base URI to look for packages to consider")
    parser.add_argument("-r", dest="rules", action="append", default=[], 
                        help="N3 rules (can specify more than once)",)
    parser.add_argument("-k", dest="api_key", help="CKAN API Key")
    parser.add_argument("-a", dest="api_base", help="CKAN API base")
    parser.add_argument("-v", dest="debug", action="store_true",
                        help="Verbose output")
    parser.add_argument("-s", dest="save", action="store_true",
                        help="Save inferred metadata back to CKAN")
    parser.add_argument("datasets", nargs="*", 
                        help="Dataset(s) to check")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    ruleStore, ruleGraph, network = makeRuleStore(args.rules)

    closureDelta = Graph()
    for dataset in args.datasets:
        network.reset(closureDelta)
        g = Graph()
        g.parse(args.base + dataset)
        network.feedFactsToAdd(generateTokenSet(g))

    if args.save:
        queue.process(base_location=args.api_base, api_key=args.api_key)

    print closureDelta.serialize(format="n3")

