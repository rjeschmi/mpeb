import mpeb

default_plugins = ( 'mpeb.web.plugins.eb' )

@mpeb.hookimpl()
def mpeb_addsubparser(parser):
    subparser = parser.addsubparser(
            'server',
            description="Run a REST server",
            help="Start a rest server"
            )
    parser.set_defaults(server=False)

@mpeb.hookimpl()
def mpeb_addoption(parser):
    subparser = parser.getsubparser('server')
    subparser.add_argument('--server-port', dest="serverport", default='3636')
    subparser.add_argument('--dburl', dest="dburl", default='sqlite://')
    subparser.set_defaults(server=True)


@mpeb.hookimpl()
def mpeb_cmdline_main(config):
    if config.option.server:
        web_port = int(config.option.serverport)
        from mpeb.web.app import get_app
        app = get_app(config)
        app.run(host='0.0.0.0', port=web_port, debug=config.option.debug)


def discover_mpeb_web_plugins(config):
    # list of plugins on command line
    # check ini for plugin path
    # check setuptools
    # default plugins
    pass
