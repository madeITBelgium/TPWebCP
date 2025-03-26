import pwd
import subprocess
from subprocess import check_output
import json
import os

from tpweb.config import get_root_dir
from tpweb.func.server import get_server_type

def do_user_exists(username):
    try:
        pwd.getpwnam(username)
    except KeyError:
        return False
    return True

def create_user_filesystem(username, password, serverId):
    serverType = get_server_type(serverId)
    if(serverType == 'main'):
        create_user_filesystem_main(username, password)
    else:
        create_user_filesystem_remote(username, password, serverId)

def create_user_filesystem_remote(username, password, serverId):
    raise Exception('Not implemented')

def create_user_filesystem_main(username, password):
    #Execute bash script to create user
    output = subprocess.run(['bash', get_root_dir() + 'bash/create-user.sh', username, password, get_root_dir()])
    if output.returncode != 0:
        raise Exception('Failed to create user')

def create_user_config(username, password, serverId):
    #create folder
    output = subprocess.run(['mkdir', get_root_dir() + 'data/' + username])
    if output.returncode != 0:
        raise Exception('Failed to create user folder')
    
    # create config files
    output = subprocess.run(['touch', get_root_dir() + 'data/' + username + '/user.conf'])
    if output.returncode != 0:
        raise Exception('Failed to create config files')
        
    #append user to file
    with open(get_root_dir() + 'data/users.conf', 'a') as file:
        file.write(str(username) + '\n')

    id = pwd.getpwnam(username).pw_uid

    # make portprefix always 4 digits
    portprefix= str(id)
    # if portprefix is less than 4 digits, add 0s to the front
    if len(portprefix) < 4:
        portprefix = '0' * (4 - len(portprefix)) + portprefix
    portprefix = str(int(portprefix[0]) + 1) + portprefix[1:]


    user = {
        'id': id,
        'portprefix': portprefix,
        'server_id': serverId,
        'username': username,
        'password': password,
        'disk_usage': 0,
        'cpu_limit': 2,
        'ram_limit': 2000,
        'disk_limit': 10000,
    }

    # write user config file
    with open(get_root_dir() + 'data/' + username + '/user.conf', 'w') as file:
        json.dump(user, file)

def get_server_id(username):
    if os.path.exists(get_root_dir() + 'data/' + username + '/user.conf'):
        with open(get_root_dir() + 'data/' + username + '/user.conf') as file:
            try:
                userJson = json.load(file)
                return userJson['server_id']
            except:
                return 1
    return 1

def delete_user(username):
    serverId = get_server_id(username)
    serverType = get_server_type(serverId)
    if(serverType == 'main'):
        delete_user_main(username)
    else:
        delete_user_remote(username, serverId)

    # delete user from this python project
    output = subprocess.run(['rm', '-r', get_root_dir() + 'data/' + username])
    #if output.returncode != 0:
    #    raise Exception('Failed to delete user')

    # delete user from users.conf
    with open(get_root_dir() + 'data/users.conf', 'r') as file:
        lines = file.readlines()
    with open(get_root_dir() + 'data/users.conf', 'w') as file:
        for line in lines:
            if line.strip("\n") != username:
                file.write(line)

def delete_user_remote(username, serverId):
    raise Exception('Not implemented')

def delete_user_main(username):
    # delete user from linux system
    subprocess.run(['killall', '-u', username, '-9'])
    subprocess.run(['docker', 'context', 'rm', username])
    subprocess.run(['systemctl', 'stop', 'docker@' + username])
    subprocess.run(['userdel', username, '--force', '--remove'])
    subprocess.run(['rm', '-rf', '/home/' + username])


def calculate_disk_usage(username):
    # calculate disk usage
    output = check_output(['du', '-s', '/home/' + username])

    return int(output.split()[0].decode('utf-8'))