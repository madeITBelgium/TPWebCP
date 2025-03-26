import os
from tpweb.config import get_root_dir
import json

def get_total_diskspace():
    return int(os.statvfs("/").f_frsize * os.statvfs("/").f_blocks / 1024 / 1024)

def get_free_diskspace():
    return int(os.statvfs("/").f_frsize * os.statvfs("/").f_bavail / 1024 / 1024)

def get_used_diskspace():
    return int(os.statvfs("/").f_frsize * (os.statvfs("/").f_blocks - os.statvfs("/").f_bfree) / 1024 / 1024)

def get_disk_status():
    return int(get_used_diskspace() / get_total_diskspace() * 100)

def get_total_users():
    count=0
    for user in os.listdir("/home"):
        if(os.path.isdir("/home/" + user + "/data")):
            count += 1
    return count

def get_total_domains():
    count=0
    for user in os.listdir("/home"):
        if(os.path.isdir("/home/" + user + "/data")):
            count += len(os.listdir("/home/" + user + "/data"))
    return count

def get_server_type(serverId):
    file = get_root_dir() + "data/servers.conf"
    with open(file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip("\n")

        id = line.split(":")[0]
        type = line.split(":")[1]

        if int(id) == serverId:
            return type
    
    return None

def get_available_server_id():
    # get server with smallest disk_status

    file = get_root_dir() + "data/servers.conf"
    with open(file, 'r') as file:
        lines = file.readlines()

    lowestDiskStatus = 100
    serverId = 1

    for line in lines:
        line = line.strip("\n")

        id = int(line.split(":")[0])

        with open(get_root_dir() + 'data/servers/' + str(id) + '.conf') as file:
            serverData = json.load(file)

        if serverData['disk_status'] < lowestDiskStatus:
            lowestDiskStatus = serverData['disk_status']
            serverId = id

    return serverId

def get_haproxy_server_id(serverId):
    # check if serverId is haproxy
    file = get_root_dir() + "data/servers/" + str(serverId) + ".conf"
    with open(file, 'r') as file:
        serverData = json.load(file)

    if serverData['isHaProxy'] == True:
        return serverId
    
    file = get_root_dir() + "data/servers.conf"
    with open(file, 'r') as file:
        lines = file.readlines()

    lowestDiskStatus = 100
    serverId = 1

    for line in lines:
        line = line.strip("\n")

        id = int(line.split(":")[0])

        with open(get_root_dir() + 'data/servers/' + str(id) + '.conf') as file:
            serverData = json.load(file)

        if serverData['isHaProxy'] == True and serverData['disk_status'] < lowestDiskStatus:
            lowestDiskStatus = serverData['disk_status']
            serverId = id

    return serverId

def get_server(id):
    with open(get_root_dir() + 'data/servers/' + str(id) + '.conf') as file:
        serverData = json.load(file)
    return serverData