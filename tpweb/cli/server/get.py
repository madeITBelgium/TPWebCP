
import sys

import json

def get(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin server get [OPTIONS] <id>")
        print()
        print("  Get server details.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    if len(args) != 1:
        print("Usage: tpweb-bin server get [OPTIONS] <id>")
        print("Error: Invalid number of arguments.")
        sys.exit(1)

    id = args[0]
    print("Getting server details for server with id:", id)

    # open server config file
    with open('data/servers/' + id + '.conf') as file:
        serverData = json.load(file)

    output = json.dumps(serverData, indent=4)
    print(output)

