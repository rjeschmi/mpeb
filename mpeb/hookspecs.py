from pluggy import HookspecMarker, HookimplMarker

hookspec = HookspecMarker('mpeb')


@hookspec(historic=True)
def mpeb_addoption(parser):
    """register arparse-style options"""
