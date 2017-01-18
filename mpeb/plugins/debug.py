import mpeb


@mpeb.hookimpl()
def mpeb_addoption(parser):
    parser.addoption("-d", "--debug", action='store_true')
