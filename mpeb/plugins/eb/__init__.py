import mpeb

@mpeb.hookimpl
def mpeb_addoption(parser):
    '''Add sub options to the main option parser'''
    parser.addoption('--eb', dest='eb', action='store_true')
    parser.addoption('--ebargs', dest='eb_args')


@mpeb.hookimpl
def mpeb_cmdline_main(config):
    if config.option.eb:
        import mpeb.plugins.eb.eb_call as eb_call
        print "called eb with args: %s" % config.option.eb_args
        eb_call.eb_call(config.option.eb_args.split())
