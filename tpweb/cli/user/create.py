
import sys

from tpweb.data.user import User

def create(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin user create [OPTIONS] <username> <password>")
        print()
        print("  Create a new user.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) != 2:
        print("Usage: tpweb-bin user create [OPTIONS] <username> <password>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    username, password = args

    user = User()
    user.create(username, password)