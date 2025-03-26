
import sys

from tpweb.data.domain import Domain
import json

def list(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin domain list [OPTIONS]")
        print()
        print("  List all domains.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    domain = Domain()
    output = domain.list()

    output = json.dumps(output, indent=4)
    print(output)