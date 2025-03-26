# Part of TPWeb CP. See LICENSE file for full copyright and licensing details.

import sys
from pathlib import Path

from .get import get
from .init import init
from .sync import sync

from tpweb.cli import Command
from tpweb.data.model import NotImplementedError



USER_HELP = """\
TPWeb CLI, use '{tpweb_bin} server --help' for regular server options.

Available commands:
    init      Initialize server configuration
    get       Get server details

Use '{tpweb_bin} user --help' for individual command help."""

def help(args):
    
    print(USER_HELP.format(  # pylint: disable=bad-builtin
        tpweb_bin=Path(sys.argv[0]).name
    ))

class Server(Command):
    """Manage server"""
    def run(self, args):
        command = "help"

        if args:
            command = args[0]
            args = args[1:]

        if command == "init":
            init(args)

        if command == "config":
            raise NotImplementedError("Not implemented yet")

        elif command == "list":
            raise NotImplementedError("Not implemented yet")

        elif command == "update":
            raise NotImplementedError("Not implemented yet")

        elif command == "get":
            get(args)

        elif command == "sync":
            sync(args)
            
        elif command == "haproxy":
            from .init import setupHaproxy
            setupHaproxy()

        else:
            help(args)