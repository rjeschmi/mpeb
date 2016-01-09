'''The mpeb plugin manager'''

import os
import logging
from ConfigParser import SafeConfigParser
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.AutoInstallPluginManager import  AutoInstallPluginManager

#Some defaults
MAIN_DIR = os.path.dirname(__file__)
CORE_PLUGIN_DIR = os.path.join(MAIN_DIR, "plugins")
CONFIG_DIR = os.path.expanduser("~/.config/mpeb")
PLUGINS_DIR = os.path.join(CONFIG_DIR, "plugins")
CONFIG_FILE = os.path.join(CONFIG_DIR, "mpeb.conf")
CONFIG_PARSER = SafeConfigParser()
CONFIG_PARSER.read(CONFIG_FILE)
PM = PluginManagerSingleton.get()

#def write_config():
#    """
#    Write the chances in the ConfigParser to a file.
#    """
#    logging.debug("Writing configuration file: %s" % CONFIG_FILE)
#    config_fh = open(self.config_file, "w")
#    CONFIG_PARSER.write(config_fh)
#    config_fh.close()

#PM.setConfigParser(CONFIG_FILE, write_config)
PM.setPluginPlaces([PLUGINS_DIR, CORE_PLUGIN_DIR])
