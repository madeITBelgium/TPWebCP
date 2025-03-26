
import sys

from tpweb.data.domain import Domain

def delete(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin domain delete [OPTIONS] <username> <domainname>")
        print()
        print("  Delete a domain.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) != 2:
        print("Usage: tpweb-bin user delete [OPTIONS] <username> <domainname>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    username = args[0]
    domainname = args[1]

    domain = Domain()
    domain.delete(username, domainname)