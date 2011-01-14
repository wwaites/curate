from setuptools import setup, find_packages
import sys, os

version = '0.9'
requirements=[
    "ckanclient",
    "pycurl",
    "rdflib",
    "FuXi>=1.2",
    ]

if sys.version_info.major == 2 and sys.version_info.minor < 7:
    requirements.append("argparse")

setup(
    name='curate',
    version=version,
    description="Curation Utilities for CKAN",
    long_description="""\
Curation Utilities for CKAN""",
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ckan rdf rdflib",
    author='Open Knowledge Foundation',
    author_email='okfn-help@lists.okfn.org',
    url="http://packages.python.org/curate/",
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    entry_points="""
        # -*- Entry points: -*-
        [console_scripts]
        curate=curate.command:curate

        [curate.builtins]

        [curate.actions]
        httpReq=curate.actions:httpReq
        curlReq=curate.actions:curlReq
#        sparqlCheck=curate.builtins:sparqlCheck
        addTag=curate.actions:addTag
        delTag=curate.actions:delTag
        addGroup=curate.actions:addGroup
    """,
)
