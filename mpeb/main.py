'''The main package that will house the function main() as the entrypoint'''

import py
import os
import sys
import argparse
import logging
import traceback

import mpeb.config as config
from mpeb.config import parseconfig
import pprint

def prepare(args):
    config = parseconfig(args)
    pprint.pprint(config)
    if config.option.help:
        show_help(config)
        raise SystemExit(0)
    return config  

def main():
    """The main sub"""
    args = sys.argv[1:]
    # Setup Parser
    config = prepare(args)
    return config.hook.mpeb_cmdline_main(config=config)


def show_help(config):
    tw = py.io.TerminalWriter()
    tw.write(config._parser._format_help())
    tw.line()
    tw.line("Environment variables", bold=True)

