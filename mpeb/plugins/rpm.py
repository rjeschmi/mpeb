
import mpeb
import importlib
from easybuild.tools.package.utilities import ActivePNS
from pprint import pprint
from easybuild.tools.run import run_cmd

@mpeb.hookimpl()
def mpeb_addoption(parser):
        parser.addoption('--try-pkg', action="store_true", dest="trypkg",
                            help = "show help message and config info")


@mpeb.hookimpl()
def mpeb_prerun_main(config):
    if config.option.trypkg:
        eb = importlib.import_module('easybuild.framework.easyblock')
        orig_func = getattr(eb.EasyBlock, 'get_steps')
        wrapped_func = runstep_wrapper(orig_func)
        setattr(eb.EasyBlock, 'get_steps', wrapped_func)
        setattr(eb.EasyBlock, 'bin_step', bin_step)

 
def bin_step(self):
    #what is rpm name?
    #send it the easyblock object
    rpmfilename = get_pkg_name(self)
    #get that rpm
    rpmfilenameurl = "http://cc.ottbioinfo.ca/eb/generic/%(rpmfilename)s" % { "rpmfilename": rpmfilename }
    #install that rpm
    cmdlist = [ 'rpm', '-iv', '--dbpath=/easybuild/rpm', rpmfilenameurl ]
    cmd = ' '.join(cmdlist)
    run_cmd(cmd, log_all=True, simple=True)
    self.skip = True

def get_pkg_name(easyblock):
    pns = ActivePNS()
    pkgname = pns.name(easyblock.cfg)
    pkgver = "eb_3.0.2"
    pkgrel = pns.release(easyblock.cfg)
    name = "%(pkgname)s-%(pkgver)s-%(pkgrel)s.x86_64.rpm" % { "pkgname": pkgname, "pkgver": pkgver, "pkgrel":pkgrel }
    return name

def runstep_wrapper(func):
    def pre():
        pass

    def post(results):
        results.insert(0, ('binary', 'install binary', [lambda x: x.bin_step], False))
        return results


    def call(*args, **kwargs):
        pre()
        results = func(*args, **kwargs)
        post_results = post(results)
        return post_results


    return staticmethod(call)
