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

default_plugins = ("eb helpconfig debug").split()

FILE_OR_DIR = 'file_or_dir'


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
    pprint.pprint(option)
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
        _a = FILE_OR_DIR
        #: a pluginmanager instance
        self.pluginmanager = pluginmanager
        self.hook = self.pluginmanager.hook
        self.option = option


    def add_cleanup(self, func):
        """ Add a function to be called when the config object gets out of
        use (usually coninciding with pytest_unconfigure)."""
        self._cleanup.append(func)

    def _do_configure(self):
        assert not self._configured
        self._configured = True
        self.hook.pytest_configure.call_historic(kwargs=dict(config=self))

    def _ensure_unconfigure(self):
        if self._configured:
            self._configured = False
            self.hook.pytest_unconfigure(config=self)
            self.hook.pytest_configure._call_history = []
        while self._cleanup:
            fin = self._cleanup.pop()
            fin()

    def warn(self, code, message, fslocation=None):
        """ generate a warning for this test session. """
        self.hook.pytest_logwarning.call_historic(kwargs=dict(
            code=code, message=message,
            fslocation=fslocation, nodeid=None))

    def get_terminal_writer(self):
        return self.pluginmanager.get_plugin("terminalreporter")._tw

    def pytest_cmdline_parse(self, pluginmanager, args):
        # REF1 assert self == pluginmanager.config, (self, pluginmanager.config)
        self.parse(args)
        return self

    def notify_exception(self, excinfo, option=None):
        if option and option.fulltrace:
            style = "long"
        else:
            style = "native"
        excrepr = excinfo.getrepr(funcargs=True,
            showlocals=getattr(option, 'showlocals', False),
            style=style,
        )
        res = self.hook.pytest_internalerror(excrepr=excrepr,
                                             excinfo=excinfo)
        if not py.builtin.any(res):
            for line in str(excrepr).split("\n"):
                sys.stderr.write("INTERNALERROR> %s\n" %line)
                sys.stderr.flush()

    def cwd_relative_nodeid(self, nodeid):
        # nodeid's are relative to the rootpath, compute relative to cwd
        if self.invocation_dir != self.rootdir:
            fullpath = self.rootdir.join(nodeid)
            nodeid = self.invocation_dir.bestrelpath(fullpath)
        return nodeid

    @classmethod
    def fromdictargs(cls, option_dict, args):
        """ constructor useable for subprocesses. """
        config = get_config()
        config.option.__dict__.update(option_dict)
        config.parse(args, addopts=False)
        for x in config.option.plugins:
            config.pluginmanager.consider_pluginarg(x)
        return config

    def _processopt(self, opt):
        for name in opt._short_opts + opt._long_opts:
            self._opt2dest[name] = opt.dest

        if hasattr(opt, 'default') and opt.dest:
            if not hasattr(self.option, opt.dest):
                setattr(self.option, opt.dest, opt.default)


    def _initini(self, args):
        ns, unknown_args = self._parser.parse_known_and_unknown_args(args, namespace=self.option.copy())
        r = determine_setup(ns.inifilename, ns.file_or_dir + unknown_args, warnfunc=self.warn)
        self.rootdir, self.inifile, self.inicfg = r
        self._parser.extra_info['rootdir'] = self.rootdir
        self._parser.extra_info['inifile'] = self.inifile
        self.invocation_dir = py.path.local()
        self._parser.addini('addopts', 'extra command line options', 'args')
        self._parser.addini('minversion', 'minimally required pytest version')

    def _consider_importhook(self, args, entrypoint_name):
        """Install the PEP 302 import hook if using assertion re-writing.

        Needs to parse the --assert=<mode> option from the commandline
        and find all the installed plugins to mark them for re-writing
        by the importhook.
        """
        ns, unknown_args = self._parser.parse_known_and_unknown_args(args)
        mode = ns.assertmode
        if mode == 'rewrite':
            try:
                hook = _pytest.assertion.install_importhook(self)
            except SystemError:
                mode = 'plain'
            else:
                import pkg_resources
                self.pluginmanager.rewrite_hook = hook
                for entrypoint in pkg_resources.iter_entry_points('pytest11'):
                    # 'RECORD' available for plugins installed normally (pip install)
                    # 'SOURCES.txt' available for plugins installed in dev mode (pip install -e)
                    # for installed plugins 'SOURCES.txt' returns an empty list, and vice-versa
                    # so it shouldn't be an issue
                    for metadata in ('RECORD', 'SOURCES.txt'):
                        for entry in entrypoint.dist._get_metadata(metadata):
                            fn = entry.split(',')[0]
                            is_simple_module = os.sep not in fn and fn.endswith('.py')
                            is_package = fn.count(os.sep) == 1 and fn.endswith('__init__.py')
                            if is_simple_module:
                                module_name, ext = os.path.splitext(fn)
                                hook.mark_rewrite(module_name)
                            elif is_package:
                                package_name = os.path.dirname(fn)
                                hook.mark_rewrite(package_name)
        self._warn_about_missing_assertion(mode)

    def _warn_about_missing_assertion(self, mode):
        try:
            assert False
        except AssertionError:
            pass
        else:
            if mode == 'plain':
                sys.stderr.write("WARNING: ASSERTIONS ARE NOT EXECUTED"
                                 " and FAILING TESTS WILL PASS.  Are you"
                                 " using python -O?")
            else:
                sys.stderr.write("WARNING: assertions not in test modules or"
                                 " plugins will be ignored"
                                 " because assert statements are not executed "
                                 "by the underlying Python interpreter "
                                 "(are you using python -O?)\n")

    def _preparse(self, args, addopts=True):
        self._initini(args)
        if addopts:
            args[:] = shlex.split(os.environ.get('PYTEST_ADDOPTS', '')) + args
            args[:] = self.getini("addopts") + args
        self._checkversion()
        entrypoint_name = 'pytest11'
        self._consider_importhook(args, entrypoint_name)
        self.pluginmanager.consider_preparse(args)
        self.pluginmanager.load_setuptools_entrypoints(entrypoint_name)
        self.pluginmanager.consider_env()
        self.known_args_namespace = ns = self._parser.parse_known_args(args, namespace=self.option.copy())
        confcutdir = self.known_args_namespace.confcutdir
        if self.known_args_namespace.confcutdir is None and self.inifile:
            confcutdir = py.path.local(self.inifile).dirname
            self.known_args_namespace.confcutdir = confcutdir
        try:
            self.hook.pytest_load_initial_conftests(early_config=self,
                    args=args, parser=self._parser)
        except ConftestImportFailure:
            e = sys.exc_info()[1]
            if ns.help or ns.version:
                # we don't want to prevent --help/--version to work
                # so just let is pass and print a warning at the end
                self._warn("could not load initial conftests (%s)\n" % e.path)
            else:
                raise

    def _checkversion(self):
        import pytest
        minver = self.inicfg.get('minversion', None)
        if minver:
            ver = minver.split(".")
            myver = pytest.__version__.split(".")
            if myver < ver:
                raise pytest.UsageError(
                    "%s:%d: requires pytest-%s, actual pytest-%s'" %(
                    self.inicfg.config.path, self.inicfg.lineof('minversion'),
                    minver, pytest.__version__))

    def parse(self, args, addopts=True):
        # parse given cmdline arguments into this config object.
        assert not hasattr(self, 'args'), (
                "can only parse cmdline args at most once per Config object")
        self._origargs = args
        self.hook.pytest_addhooks.call_historic(
                                  kwargs=dict(pluginmanager=self.pluginmanager))
        self._preparse(args, addopts=addopts)
        # XXX deprecated hook:
        self.hook.pytest_cmdline_preparse(config=self, args=args)
        args = self._parser.parse_setoption(args, self.option, namespace=self.option)
        if not args:
            cwd = os.getcwd()
            if cwd == self.rootdir:
                args = self.getini('testpaths')
            if not args:
                args = [cwd]
        self.args = args


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


