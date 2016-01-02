"""A sub-command"""

from yapsy.IPlugin import IPlugin

class channel(IPlugin):
    def set_options(self, subparsers):
        channel_parser = subparsers.add_parser('channel', help="A command to set plugin channels")
        channel_parser.set_defaults(func=self.call_channel)
        print "Setting channel options"

    def call_channel(self, args):
        print "called channel %s" % args
