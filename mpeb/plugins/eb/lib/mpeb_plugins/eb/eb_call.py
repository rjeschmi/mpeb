"""A script that is run within docker to handle building a specific repo"""

import os
import sys
import argparse
import glob
import subprocess
import importlib

from subprocess import check_call, PIPE
from multiprocessing import Process


def module(command, arguments=[]):
    cmd = ['/software/Lmod/lmod/lmod/libexec/lmod', 'python'] + [command] + arguments
    try:
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = process.communicate()
        # print "stdout: %s stderr: %s" % (stdout, stderr)
        exec stdout #pylint: disable=W0122
    except Exception, err:
        print "Caught Exception err: %s in cmd: %s" % (err, cmd)
        sys.exit(1)

def update_sys_path():
    sys.path.extend(os.environ['PYTHONPATH'].split(os.pathsep))

def path_addto(destpath, srcpath):
    if os.getenv(destpath):
        os.environ[destpath] += os.pathsep + srcpath
    else:
        os.environ[destpath] = srcpath
    # print "environ: %s" % os.environ

def eb_main_call(*args, **kwargs):
    """A function that will be demoted and call eb_main_call"""
    #demote()()
    args = kwargs.get('args', None)
    import easybuild.main as eb_main
    eb_main.main(args=args)

def eb_call(arguments, *args, **kwargs):
    opt_args = []
    try:
        eb_kwargs = {'args': arguments}
        process = Process(target=eb_main_call, kwargs=eb_kwargs)
        process.start()
        process.join()
    except Exception, err:
        print "Caught Exception err: %s" % (err)
        sys.exit(1)

def demote():
    def set_ids():
        os.setgid(1000)
        os.setuid(1000)
    return set_ids


def add_hooks(module):
    '''Add module_pre and module_post hooks'''

     
