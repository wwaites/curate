"""
.. program:: curate

Tool for curation of CKAN datasets. It reads RDF descriptions
of the dataset and applies the specified rules. Inferred 
statements are written to the standard output in Notation 3
and built-in predicates may be used to check specific conditions
or perform certain actions.

Usage: ``curate [options] [dataset [dataset [...]]]``

.. cmdoption:: -b base_uri

    Base URI to read dataset descriptions from. The RDF graph
    at ${base_uri}/${dataset} is read for each dataset and 
    passed as input to the inference rules.

.. cmdoption:: -a api_base

    Base URI for calls to the CKAN API. This is useful for
    running the tool against different CKAN instances.

.. cmdoption:: -r rules

    Inference rules in Notation 3 to read. May be specified
    multiple times

.. cmdoption:: -k api_key

    CKAN API Key to use where authentication is required

.. cmdoption:: -s

    Save any inferred dataset metadata to the CKAN instance.
    If this is not specified the program will run and perform all
    checks but will not actually perform any operations via the
    CKAN api.

.. cmdoption:: -l

    Log information to file
    
.. cmdoption:: -v

    Verbose output

.. cmdoption:: -h, --help

    output a help message

"""

import argparse
import re

import warnings
warnings.simplefilter("ignore", DeprecationWarning)
import logging

from curate.rules import makeRuleStore
from rdflib.Graph import Graph
from FuXi.Rete.Util import generateTokenSet
from ckanclient import CkanClient
from curate.work import queue

_uri_re = re.compile(r"^[a-zA-Z]+:")
def is_uri(u):
    return _uri_re.match(u) is not None

def curate():
    parser = argparse.ArgumentParser(description="""
Tool for curation of CKAN datasets. It reads RDF descriptions
of the dataset and applies the specified rules. Inferred 
statements are written to the standard output in Notation 3
and built-in predicates may be used to check specific conditions
or perform certain actions.
""")
    parser.add_argument("-b", dest="base", default="http://semantic.ckan.net/package/",
                        help="RDF description base URI to look for packages to consider")
    parser.add_argument("-r", dest="rules", action="append", default=[], 
                        help="N3 rules (can specify more than once)",)
    parser.add_argument("-k", dest="api_key", help="CKAN API Key")
    parser.add_argument("-a", dest="api_base", help="CKAN API base")
    parser.add_argument("-d", dest="delta", action="store_true", 
                        help="Accumulate closure delta")
    parser.add_argument("-l", dest="logfile", help="Log to file")
    parser.add_argument("-v", dest="debug", action="store_true",
                        help="Verbose output")
    parser.add_argument("-s", dest="save", action="store_true",
                        help="Save inferred metadata back to CKAN")
    parser.add_argument("datasets", nargs="*", 
                        help="Dataset(s) to check")
    args = parser.parse_args()

    logcfg = {
        "level": logging.DEBUG if args.debug else logging.INFO,
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    }
    if args.logfile:
        logcfg["filename"] = args.logfile
    logging.basicConfig(**logcfg)

    log = logging.getLogger(__name__)

    ruleStore, ruleGraph, network = makeRuleStore(args.rules)

    datasets = args.datasets
    if not datasets:
        datasets = CkanClient(base_location=args.api_base, api_key=args.api_key
                              ).package_register_get()

    closureDelta = Graph()
    for dataset in datasets:
        log.info("processing %s" % dataset)
        network.reset(closureDelta)
        if not is_uri(dataset):
            dataset = args.base + dataset
        try:
            g = Graph()
            g.parse(dataset)
        except Exception, e:
            log.error("exception loading graph at %s" % (args.base+dataset,))
            continue
        network.feedFactsToAdd(generateTokenSet(g))

        if args.save:
            queue.process(base_location=args.api_base, api_key=args.api_key)

        if not args.delta:
            closureDelta = Graph()


    if args.delta:
        print closureDelta.serialize(format="n3")

