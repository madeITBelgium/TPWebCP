
import sys

from tpweb.data.user import User
import json
import os
import subprocess
import socket
import urllib.request
from tpweb.func.server import get_total_diskspace, get_free_diskspace, get_used_diskspace, get_disk_status
import requests

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_ipv6():
    ipv6 = subprocess.check_output(["ip", "addr", "show"]).decode("utf-8")
    ipv6 = ipv6.split("\n")
    for line in ipv6:
        if "inet6" in line and not "fe80" in line:
            ipv6 = line.split(" ")[1]
            break
    return ipv6

def init(args):
    # if args contains --help
    if "--help" in args:
        print("Usage: tpweb-bin server init [OPTIONS]")
        print()
        print("  Initialize server configuration")
        print()
        print("Options:")
        print("  --main    Configure main server")
        print("  --worker  Configure worker server")
        print("  --help    Show this message and exit.")
        sys.exit(0)

    # if args contains --main
    if "--main" in args:
        print("Start configuring main server")

        ipv6 = get_ipv6()
        ipv4 = get_ip()
        f = urllib.request.urlopen("https://cp.madeit.be/my-ip.php")
        ipv4Public = f.read().decode("utf-8")
        hostname=socket.gethostname()

        print("IPv6 address: " + ipv6)
        print("IPv4 address: " + ipv4)
        print("Public IPv4 address: " + ipv4Public)

        hasHaProxy = False
        # Check if haproxy folder exists
        if os.path.exists("haproxy"):
            hasHaProxy = True
        
        hasPowerDNS = False
        isDnsMaster = False
        if os.path.exists("powerdns"):
            hasPowerDNS = True
            isDnsMaster = True

        # Create .env file
        with open(".env", "w") as f:
            f.write("ROOT_DIR=" + os.getcwd() + "\n")
            f.write("SERVER_TYPE=main\n")
            f.write("IPV6=" + ipv6 + "\n")
            f.write("IPV4=" + ipv4 + "\n")
            f.write("IPV4_PUBLIC=" + ipv4Public + "\n")
            f.write("IP_PROXY=" + ipv4Public + "\n")
            f.write("IP6_PROXY=" + ipv6 + "\n")
            f.write("HOSTNAME=" + hostname + "\n")
            f.write("IS_HAPROXY=" + str(hasHaProxy) + "\n")
            f.write("IS_POWERDNS=" + str(hasPowerDNS) + "\n")
            f.write("IS_DNS_MASTER=" + str(isDnsMaster) + "\n")

        # create empty users.conf file
        with open("data/users.conf", "w") as f:
            f.write("")

        # create empty domains.conf file
        with open("data/domains.conf", "w") as f:
            f.write("")

        # create empty servers.conf file
        with open("data/servers.conf", "w") as f:
            f.write("")

        # create server directory
        #os.mkdir("data/servers")

        serverInfo = {
            "id": 1,
            "type": "main",
            "ipv6": ipv6,
            "ipv4": ipv4,
            "ipv4Public": ipv4Public,
            "hostname": hostname,
            'ipProxy': ipv4Public,
            'ip6Proxy': ipv6,
            'isHaProxy': hasHaProxy,
            'isPowerDns': hasPowerDNS,
            'isDnsMaster': isDnsMaster,
            'count_users': 0,
            'count_domains': 0,
            'disk_usage': get_used_diskspace(),
            'disk_limit': get_total_diskspace(),
            'disk_status': get_disk_status(),
        }

        # create server config file
        with open("data/servers/1.conf", "w") as f:
            f.write(json.dumps(serverInfo, indent=4))

        with open("data/servers.conf", "w") as f:
            f.write("1:main:" + hostname + "\n")
        
    # if args contains --worker
    elif "--worker" in args:
        print("Start configuring worker server")

        ipv6 = get_ipv6()
        ipv4 = get_ip()
        f = urllib.request.urlopen("https://cp.madeit.be/my-ip.php")
        ipv4Public = f.read().decode("utf-8")

        print("IPv6 address: " + ipv6)
        print("IPv4 address: " + ipv4)
        print("Public IPv4 address: " + ipv4Public)

        masterIp = input("Enter the IP address of the master server: ")
        masterKey = input("Enter the master key: ")

        # Todo: Connect to the master server


        hasHaProxy = False
        # Check if haproxy folder exists
        if os.path.exists("haproxy"):
            hasHaProxy = True
        
        hasPowerDNS = False
        isDnsMaster = False
        if os.path.exists("powerdns"):
            hasPowerDNS = True
            isDnsMaster = True

        # Create .env file
        with open(".env", "w") as f:
            f.write("ROOT_DIR=" + os.getcwd() + "\n")
            f.write("SERVER_TYPE=worker\n")
            f.write("IPV6=" + ipv6 + "\n")
            f.write("IPV4=" + ipv4 + "\n")
            f.write("IPV4_PUBLIC=" + ipv4Public + "\n")
            f.write("MASTER_IP=" + masterIp + "\n")
            f.write("MASTER_KEY=" + masterKey + "\n")
            #todo add haproxy and powerdns

    else:
        print("Invalid option")
        sys.exit(1)

def randomPassword(length):
    import random
    import string
    # generate random password
    password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))
    return password
