
import sys

from tpweb.data.domain import Domain, DomainDoesNotExistError
import json

def get(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin domain get [OPTIONS] <domainname>")
        print()
        print("  Get domain information.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) != 1:
        print("Usage: tpweb-bin domain get [OPTIONS] <domainname>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    username = args[0]

    domain = Domain()
    try:
        output = domain.get(username)
    except DomainDoesNotExistError:
        print("Error: Domain %s does not exist." % username)
        sys.exit(1)


    output = json.dumps(output, indent=4)
    print(output)