
import sys

import subprocess
from tpweb.func.server import get_total_diskspace, get_free_diskspace, get_used_diskspace, get_disk_status

def update(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin server update")
        print()
        print("  Update TPWeb CP")
        sys.exit(0)

    # go to tpweb directory, and run git pull
    # git pull
    output = subprocess.check_output(["git", "pull"]).decode("utf-8")
    print(output)
    print("TPWeb CP updated")