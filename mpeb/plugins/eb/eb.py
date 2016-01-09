"""A sub-command"""
import os, sys
import logging
from yapsy.IPlugin import IPlugin


class EB(IPlugin):
    '''Setup a channel to track plugins from a remote location'''

    def set_options(self, subparsers):
        '''Add sub options to the main option parser'''
        eb_parser = subparsers.add_parser('eb', help="A command to call eb")
        eb_parser.add_argument('eb_args', nargs='+')

        eb_parser.set_defaults(func=self.call_eb)
        print "Setting channel options"

    def append_sys_path(self):
        '''Append the global syspath relative to this file'''
        sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
        logging.debug("Added to path now: %s", sys.path)

    def call_eb(self, args):
        '''This is the function called by the sub command'''
        self.append_sys_path()
        import mpeb_plugins.eb.eb_call as eb_call
        print "called eb with args: %s" % args.eb_args
        eb_call.eb_call(args.eb_args)
