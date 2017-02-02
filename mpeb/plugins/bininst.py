import mpeb
import rpm 
import importlib
from pprint import pprint

@mpeb.hookimpl()
def mpeb_addoption(parser):
        subparser = parser.getsubparser('eb')
        subparser.add_argument('--try-pkg', action="store_true", dest="trypkg",
                            help = "show help message and config info")


@mpeb.hookimpl()
def mpeb_prerun_main(config):
    if config.option.eb and config.option.trypkg:
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
    rpmpath = self.obtain_file(rpmfilenameurl)
    if rpmpath:
        self.log.info("Installing rpm %s" % rpmpath)
        rpm.addMacro('_dbpath', '/easybuild/rpm')
        ts = rpm.TransactionSet()
        ts.addInstall(rpmpath, rpmpath, 'u')
        ts.check()
        self.log.info("starting run")
        rpmtrans = RPMTrans()
        res = ts.run(rpmtrans.callback, '')
        if res is None:
            self.log.info("rpm install success")
            self.skip = True
            self.cfg['skipsteps'].append('package')
        else:
            pprint(res)
    else:
        self.log.info("no rpm found, skipping")

class RPMTrans:
    def callback(self, what, amount, total, key, client_data):
        if what == rpm.RPMCALLBACK_TRANS_START:
            pass 
        elif what == rpm.RPMCALLBACK_TRANS_STOP:
            pass 
        elif what == rpm.RPMCALLBACK_INST_OPEN_FILE:
            try:
                self.fd=open(key)
            except IOError as e:
                print "canot open file"
            return self.fd.fileno()

        elif what == rpm.RPMCALLBACK_INST_CLOSE_FILE:
            self.fd.close()
            self.fd = None



def get_pkg_name(easyblock):
    from easybuild.tools.package.utilities import ActivePNS
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
        for i, step in enumerate(results):
            if results[i][0] == 'package':
                package_step = list(results.pop(i))
                package_step[3] = True
                results.insert(i, tuple(package_step))
        #pprint (results)
        return results


    def call(*args, **kwargs):
        pre()
        results = func(*args, **kwargs)
        post_results = post(results)
        return post_results


    return staticmethod(call)
