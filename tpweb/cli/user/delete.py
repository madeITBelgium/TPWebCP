
import sys

from tpweb.data.user import User

def delete(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin user delete [OPTIONS] <username>")
        print()
        print("  Delete a user.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) != 1:
        print("Usage: tpweb-bin user delete [OPTIONS] <username>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    username = args[0]

    user = User()
    user.delete(username)