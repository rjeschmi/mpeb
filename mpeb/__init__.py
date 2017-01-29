import logging

from .hookspecs import hookspec, hookimpl  # noqa

# set up logging to file - see previous section for more details
#logging.basicConfig(level=logging.WARN)
# define a Handler which writes INFO messages or higher to the sys.stderr
#console = logging.StreamHandler()
#console.setLevel(logging.INFO)
# set a format which is simpler for console use
#formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
#console.setFormatter(formatter)
# add the handler to the root logger

#logging.getLogger('').addHandler(console)

class exception:
    class Error(Exception):
        def __str__(self):
            return "%s: %s" % ( self.__class__.__name__, self.args[0])

    class MPEBException(Error):
        """generic exception"""
