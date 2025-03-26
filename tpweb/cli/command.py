# Part of TPWeb CP. See LICENSE file for full copyright and licensing details.

import sys
from pathlib import Path
from tpweb.config import has_config

commands = {}
class Command:
    name = None
    def __init_subclass__(cls):
        cls.name = cls.name or cls.__name__.lower()
        commands[cls.name] = cls


TPWEB_HELP = """\
TPWeb CLI, use '{tpweb_bin} --help' for regular server options.

Available commands:
    {command_list}

Use '{tpweb_bin} <command> --help' for individual command help."""

class Help(Command):
    """ Display the list of available commands """
    def run(self, args):
        padding = max([len(cmd) for cmd in commands]) + 2
        command_list = "\n    ".join([
            "    {}{}".format(name.ljust(padding), (command.__doc__ or "").strip())
            for name, command in sorted(commands.items())
        ])
        print(TPWEB_HELP.format(  # pylint: disable=bad-builtin
            tpweb_bin=Path(sys.argv[0]).name,
            command_list=command_list
        ))

def main():
    args = sys.argv[1:]

    # Default legacy command
    command = "help"

    # Subcommand discovery
    if len(args) and not args[0].startswith("-"):
        command = args[0]
        args = args[1:]

    if not has_config():
        if(command == 'init'):
            from tpweb.cli.server.init import init
            init(args)
            return
        
        print('No instance found. Please run tpweb init')
        return


    if command in commands:
        o = commands[command]()
        o.run(args)
    else:
        sys.exit('Unknown command %r' % (command,))