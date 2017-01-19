from pluggy import HookspecMarker, HookimplMarker

hookspec = HookspecMarker("mpeb")
hookimpl = HookimplMarker("mpeb")

@hookspec()
def mpeb_addoption(parser):
    """register arparse-style options"""

@hookspec()
def mpeb_cmdline_main(config):
    """the run loop"""

@hookspec()
def mpeb_prerun_main(config):
    """wrap things here"""
