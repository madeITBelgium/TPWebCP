
import sys
import json

from tpweb.config import get_root_dir
from tpweb.func.server import get_total_diskspace, get_free_diskspace, get_used_diskspace, get_disk_status, get_total_users, get_total_domains


def sync(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin server sync [OPTIONS]")
        print()
        print("  Sync server details.")
        print()
        print("Options:")
        print("  --help  Show this message and exit.")
        sys.exit(0)

    # get all servers from config
    file = get_root_dir() + "data/servers.conf"
    with open(file, 'r') as file:
            lines = file.readlines()

    for line in lines:
        line = line.strip("\n")

        id = line.split(":")[0]
        type = line.split(":")[1]
        hostname = line.split(":")[2]

        print("Syncing server with id:", id)

        # open server config file
        with open(get_root_dir() + 'data/servers/' + id + '.conf') as file:
            serverData = json.load(file)

        if (type == 'main'):
            # get disk space
            serverData['count_users'] = get_total_users()
            serverData['count_domains'] = get_total_domains()
            serverData['disk_usage'] = get_used_diskspace()
            serverData['disk_limit'] = get_total_diskspace()
            serverData['disk_status'] = get_disk_status()
        else:
            # TODO: Get remote server details
            pass

        # write server config file
        with open(get_root_dir() + 'data/servers/' + id + '.conf', 'w') as file:
            file.write(json.dumps(serverData, indent=4))


