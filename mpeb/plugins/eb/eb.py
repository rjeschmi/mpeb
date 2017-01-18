"""A sub-command"""
import os, sys
import logging
from mpeb.pluginmanager import ICLIPlugin


class EB(Object):
    '''Setup a channel to track plugins from a remote location'''

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
