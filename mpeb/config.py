""" command line options, ini-file and conftest.py processing. """
import argparse
import shlex
import traceback
import types
import warnings

import py
# DON't import pytest here because it causes import cycle troubles
import sys, os
import pluggy
from   mpeb.parser import Parser
import mpeb.hookspecs
import importlib

import pprint

default_plugins = ("eb rpm helpconfig debug").split()



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
    parser = Parser()
    pm.hook.mpeb_addoption(parser=parser)

    # parse command line options
    option = parser._parse_args(args)
    config = Config(pluginmanager=pm, option=option)
    config._parser = parser

    return config


def _prepareconfig(args=None, plugins=None):
    warning = None
    if args is None:
        args = sys.argv[1:]
    elif isinstance(args, py.path.local):
        args = [str(args)]
    elif not isinstance(args, (tuple, list)):
        if not isinstance(args, str):
            raise ValueError("not a string or argument list: %r" % (args,))
        args = shlex.split(args, posix=sys.platform != "win32")
        from _pytest import deprecated
        warning = deprecated.MAIN_STR_ARGS
    config = get_config()
    pluginmanager = config.pluginmanager
    try:
        if plugins:
            for plugin in plugins:
                if isinstance(plugin, py.builtin._basestring):
                    pluginmanager.consider_pluginarg(plugin)
                else:
                    pluginmanager.register(plugin)
        if warning:
            config.warn('C1', warning)
        return pluginmanager.hook.pytest_cmdline_parse(
                pluginmanager=pluginmanager, args=args)
    except BaseException:
        config._ensure_unconfigure()
        raise


class Config(object):
    """ access to configuration values, pluginmanager and plugin hooks.  """

    def __init__(self, pluginmanager, option):
        #: a pluginmanager instance
        self.pluginmanager = pluginmanager
        self.hook = self.pluginmanager.hook
        self.option = option


    def get_terminal_writer(self):
        return self.pluginmanager.get_plugin("terminalreporter")._tw


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


