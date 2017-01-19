''' help and config options '''

import mpeb


@mpeb.hookimpl()
def mpeb_addoption(parser):
    parser.addoption('-h', '--help', action="store_true", dest="help",
            help = "show help message and config info")

