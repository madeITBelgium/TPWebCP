# Part of TPWeb CP. See LICENSE file for full copyright and licensing details.

import sys
from pathlib import Path

from .create import create
from .delete import delete
from .list import list
from .disk import calculate
from .get import get
from tpweb.cli import Command


USER_HELP = """\
TPWeb CLI, use '{tpweb_bin} user --help' for regular server options.

Available commands:
    create    Create a new user
    delete    Delete a user
    list      List users
    get       Get user details
    calcdisk  Calculate disk usage

Use '{tpweb_bin} user --help' for individual command help."""

def help(args):
    
    print(USER_HELP.format(  # pylint: disable=bad-builtin
        tpweb_bin=Path(sys.argv[0]).name
    ))

class User(Command):
    """Manage users"""
    def run(self, args):
        command = "help"

        if args:
            command = args[0]
            args = args[1:]

        if command == "create":
            create(args)

        elif command == "delete":
            delete(args)

        elif command == "list":
            list(args)

        elif command == "calcdisk":
            calculate(args)

        elif command == "get":
            get(args)

        else:
            help(args)