'''The main package that will house the function main() as the entrypoint'''

import os
import sys
import argparse
import logging
from mpeb.pluginmanager import PM


def main():
    """The main sub"""
    args = sys.argv[1:]
    # Setup Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true')
    subparsers = parser.add_subparsers(help='sub-command help')
    PM.collectPlugins()
    for plugin in PM.getPluginsOfCategory("cli"):
        print "loading plugins %s" % plugin.name
        plugin.plugin_object.set_options(subparsers)

    args = parser.parse_args()
    print "args: %s" % args
    if args.debug == True:
        logging.basicConfig(level=logging.DEBUG)

    args.func(args)
