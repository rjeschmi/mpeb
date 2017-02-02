import mpeb

@mpeb.hookimpl
def mpeb_addoption(parser):
    parser.adoption('--db-url', dest='dpath', default='sqlite://')


@mpeb.hookimpl()
def mpeb_
