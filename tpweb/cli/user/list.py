
import sys

from tpweb.data.user import User
import json

def list(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin user list [OPTIONS]")
        print()
        print("  List all users.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    user = User()
    output = user.list()

    output = json.dumps(output, indent=4)
    print(output)