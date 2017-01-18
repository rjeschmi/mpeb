'''The main package that will house the function main() as the entrypoint'''

import os
import sys
import argparse
import logging
import mpeb.config as config

def prepare(args):
    

def main():
    """The main sub"""
    args = sys.argv[1:]
    # Setup Parser
    try: 
        config = prepare(args)parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true')
    subparsers = parser.add_subparsers(help='sub-command help')
    pm.get_plugin_manager()
    pm.hook.mpeb_set_options()

    args = parser.parse_args()
    print "args: %s" % args
    if args.debug == True:
        logging.basicConfig(level=logging.DEBUG)

    args.func(args)
