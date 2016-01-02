'''The main package that will house the function main() as the entrypoint'''

import os
import sys
import argparse
import mpeb.pluginmanager

MAIN_DIR = os.path.dirname(__file__)
CORE_PLUGIN_DIR = os.path.join(MAIN_DIR, "plugins")
CONFIG_DIR = os.path.expanduser("~/.config/mpeb")
PLUGINS_DIR = os.path.join(CONFIG_DIR, "plugins")

PluginManager = mpeb.pluginmanager.MpebPluginManager.get()
PluginManager.setPluginPlaces([PLUGINS_DIR, CORE_PLUGIN_DIR])
print "looking for plugins in %s " % [PLUGINS_DIR, CORE_PLUGIN_DIR]
def main():
    """The main sub"""
    args = sys.argv[1:]
    #Setup Parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    PluginManager.collectPlugins()
    for plugin in PluginManager.getAllPlugins():
        print "loading plugins"
        plugin.plugin_object.set_options(subparsers)

    args = parser.parse_args()
    args.func(args)
