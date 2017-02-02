""" command line options, ini-file and conftest.py processing. """
import argparse
import warnings

import py
# DON't import pytest here because it causes import cycle troubles
import sys, os

FILE_OR_DIR = 'file_or_dir'


class Parser:
    """ Parser for command line arguments and ini-file values.

    :ivar extra_info: dict of generic param -> value to display in case
        there's an error processing the command line arguments.
    """

    def __init__(self, subparser=False):
        self.argparser = argparse.ArgumentParser(
                 description="mpeb options", add_help=False)
        if subparser:
            self.subparsers = self.argparser.add_subparsers()
            self.subparser = {}

    def addoption(self, *args, **kwargs):
        """ add argument to command line parser.  This takes the
        same arguments that ``argparse.ArgumentParser.add_argument``.
        """
        return self.argparser.add_argument(*args, **kwargs)

    def addsubparser(self, title, description=None, help=None ):
        self.subparser[title]=self.subparsers.add_parser(title, description=description)
        return self.subparser[title]

    def getsubparser(self, title):
        return self.subparser[title]

    def set_defaults(self, *args, **kwargs):
        self.argparser.set_defaults(*args, **kwargs)

    def _parse_args(self, args):
        self.namespace, self.extra = self.argparser.parse_known_args(args)
        return self.namespace

    def _format_help(self):
        return self.argparser.format_help()

