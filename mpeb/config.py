""" command line options, ini-file and conftest.py processing. """
import argparse
import shlex
import traceback
import types
import warnings
import logging
import py
# DON't import pytest here because it causes import cycle troubles
import sys, os
import pluggy
from   mpeb.parser import Parser
import mpeb.hookspecs
import importlib

import pprint

default_plugins = ("eb bininst helpconfig debug server").split()



def get_plugin_manager(plugins=()):
    pm = pluggy.PluginManager("mpeb")
    pm.add_hookspecs(mpeb.hookspecs)
    pm.register(mpeb.config)
    for plugin in default_plugins:
        importspec = "mpeb.plugins.%s" % plugin
        try:
            mpebplugin = importlib.import_module(importspec)
        except ImportError as e:
            new_exc = ImportError('Error importing plugin "%s": %s' % (plugin, str(e.args[0])))
            raise new_exc

        pm.register(mpebplugin)
    pm.load_setuptools_entrypoints("mpeb")
    for plugin in plugins:
        pm.register(plugin)
    pm.check_pending()
    return pm

def parseconfig(args=None, plugins=()):
    """
    :param list[str] args: Optional list of arguments.
    :type pkg: str
    :rtype: :class:`Config`
    :raise SystemExit: toxinit file is not found
    """

    pm = get_plugin_manager(plugins)

    if args is None:
        args = sys.argv[1:]

    # prepare command line options
    parser = Parser(subparser=True)
    pm.hook.mpeb_addsubparser(parser=parser)
    pm.hook.mpeb_addoption(parser=parser)

    # parse command line options
    option = parser._parse_args(args)
    config = Config(pluginmanager=pm, option=option)
    config._parser = parser
    config.extraargs = parser.extra

    return config

class Config(object):
    """ access to configuration values, pluginmanager and plugin hooks.  """

    def __init__(self, pluginmanager, option):
        #: a pluginmanager instance
        self.pluginmanager = pluginmanager
        self.hook = self.pluginmanager.hook
        self.option = option
        self.ebcfg = {}
        self.detopts = ( 'prefix', 'optarch', 'module-naming-scheme' )
        
        if self.option.eb and self.option.ebargs:
            ebcfg = py.path.local(self.option.ebcfg)
            if not ebcfg.check():
                raise mpeb.exception.MPEBException("couldn't find %s" % ebcfg)
            self.inicfg = py.iniconfig.IniConfig(self.option.ebcfg)
            for opt in self.detopts:
                try:
                    self.ebcfg[opt] =  self.inicfg['easybuild'][opt]
                except KeyError:
                    print "missing opt %s" % opt
        console = logging.StreamHandler()
        self.log = logging.getLogger('mpeb')
        if self.option.debug:
            console.setLevel(logging.DEBUG)
            self.log.setLevel(logging.DEBUG)
        else:
            console.setLevel(logging.INFO)
            self.log.setLevel(logging.INFO)

        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        self.log.addHandler(console)
        self.log.info("Logging Set Up")

    def get_terminal_writer(self):
        return self.pluginmanager.get_plugin("terminalreporter")._tw

    def get_sqlalchemy_url(self):
        if self.option.dburl:
            return self.option.dburl
        elif self.inicfg['server']['dburl']:
            return self.inicfg['server']['dburl']
        else:
            SystemExit("Cannot find DBURL")

    def get_debug(self):
        self.log.debug("getting debug %s", self.option)
        return self.option.debug

def create_terminal_writer(config, *args, **kwargs):
    """Create a TerminalWriter instance configured according to the options
    in the config object. Every code which requires a TerminalWriter object
    and has access to a config object should use this function.
    """
    tw = py.io.TerminalWriter(*args, **kwargs)
    if config.option.color == 'yes':
        tw.hasmarkup = True
    if config.option.color == 'no':
        tw.hasmarkup = False
    return tw


