
import sys

from tpweb.data.user import User
import json

def get(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin user get [OPTIONS] <username>")
        print()
        print("  Get user details.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) != 1:
        print("Usage: tpweb-bin user get [OPTIONS] <username>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    username = args[0]

    user = User()
    output = user.get(username)

    output = json.dumps(output, indent=4)
    print(output)