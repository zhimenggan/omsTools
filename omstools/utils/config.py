#!/usr/bin/env python

""" omsTools config module. """

import pkg_resources

# gtf tools
# GTF tools includes class, functions and dicts from assemblyline
gtf_tools = dict()
for entry_point in pkg_resources.iter_entry_points('gtf'):
    gtf_tools.update({entry_point.name: entry_point.load()})