import mpeb


@mpeb.hookimpl()
def mpeb_addoption(parser):
    parser.addoption("-d", "--debug", dest="debug", action='store_true')
