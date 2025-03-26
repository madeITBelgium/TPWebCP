
import sys

from tpweb.data.user import User
import json

from tpweb.func.user import calculate_disk_usage


def calculate(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin user calcdisk [OPTIONS] <username>")
        print()
        print("  Calculate disk usage for a user.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) != 1:
        print("Usage: tpweb-bin user delete [OPTIONS] <username>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    username = args[0]

    diskusage = calculate_disk_usage(username) / 1024

    user = User()
    user.update(username, disk_usage=diskusage)