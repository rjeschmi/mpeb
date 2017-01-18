
def mpeb_addoptions(parser):
    '''Add sub options to the main option parser'''
    eb_parser = parser.add_parser('eb', help="A command to call eb")
    eb_parser.add_argument('eb_args', nargs='+')

    print "Setting eb options"

def mpeb_cmdline_main(config):
    if config.option.eb
        import mpeb.plugins.eb.eb_call as eb_call
        print "called eb with args: %s" % config.option.eb_args
        eb_call.eb_call(config)
