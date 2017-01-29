import mpeb

@mpeb.hookimpl
def mpeb_setup():
    '''Pre-config setup, check for things that matter'''
    try:
        import easybuild.main
    except ImportError as err:
        raise SystemExit("Unable to find EasyBuild, you may nead to load it using `module load Easybuild.` Exiting")

@mpeb.hookimpl
def mpeb_addoption(parser):
    '''Add sub options to the main option parser'''
    subparser = parser.addsubparser(
                    'eb', 
                    description="Lets run an EasyBuild instance",
                    help="If you want to run easybuild commands, run this",
                    )
    subparser.add_argument('--eb-demote', dest='demote', action='store_true')
    subparser.add_argument('--ebargs', dest='eb_args')
    subparser.add_argument('--ebcfg')
    subparser.set_defaults(eb=True)


@mpeb.hookimpl
def mpeb_cmdline_main(config):
    if config.option.eb:
        import mpeb.plugins.eb.eb_call as eb_call
        print "called eb with args: %s" % config.option.eb_args
        call_args = []
        if config.option.eb_args:
            call_args = config.option.eb_args.split()
        elif(config.extraargs is not None):
            call_args = config.extraargs
            print "setting call_args: %s" % call_args
        else:
            raise SystemExit("Couldn't find any arguments to pass EasyBuild")
        eb_call.eb_call(call_args, config.option.demote)
