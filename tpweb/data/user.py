from .model import Model
import json
import os

from tpweb.func.user import do_user_exists, create_user_filesystem, create_user_config, delete_user
from tpweb.func.server import get_available_server_id

from tpweb.config import get_root_dir
from .domain import Domain

class User(Model):
    name = 'user'
    path = 'user'

    def list(self):
        # open file and list all users
        file = get_root_dir() + 'data/users.conf'

        # read file line by line
        with open(file, 'r') as file:
            lines = file.readlines()

        # append each line to json output object
        users = []
        for line in lines:
            # add user to users object as key value pair
            user = line.strip("\n")
            userData = {
                'username': user,
            }

            # read user config file
            with open(get_root_dir() + 'data/' + user + '/user.conf') as file:
                userJson = json.load(file)

            userData['password'] = userJson['password']
            userData['disk_usage'] = userJson['disk_usage']
            userData['cpu_limit'] = userJson['cpu_limit']
            userData['ram_limit'] = userJson['ram_limit']
            userData['disk_limit'] = userJson['disk_limit']

            domains = []
            #ls all directories in user directory get_root_dir() + 'data/' + user + '/domains'
            domainLines = os.listdir(get_root_dir() + 'data/' + user + '/domains')


            # append each line to json output object
            for domainLine in domainLines:
                domain = domainLine.strip("\n")
                domains.append(domain)
                
            userData['domains'] = domains

            users.append({user: userData})

        return users

    def get(self, username):
        #check if user exists
        if(do_user_exists(username) == False):
            raise UserExistsError('User does not exist')

        with open(get_root_dir() + 'data/' + username + '/user.conf') as file:
            userJson = json.load(file)

        userData = {
            'username': username,
            'password': userJson['password'],
            'disk_usage': userJson['disk_usage'],
            'cpu_limit': userJson['cpu_limit'],
            'ram_limit': userJson['ram_limit'],
            'disk_limit': userJson['disk_limit'],
            'portprefix': userJson['portprefix'],
        }

        domains = []
        if os.path.exists(get_root_dir() + 'data/' + username + '/domains.conf'):
            # open user config file
            with open(get_root_dir() + 'data/' + username + '/domains.conf', 'r') as file:
                domainLines = file.readlines()

            # append each line to json output object
            for domainLine in domainLines:
                domain = domainLine.strip("\n")
                domains.append(domain)

        userData['domains'] = domains

        return userData

    def create(self, username, password):
        # check if user already exists on linux system

        if(do_user_exists(username) == True):
            raise UserExistsError('User already exists')

        serverId = get_available_server_id()

        create_user_filesystem(username, password, serverId)

        create_user_config(username, password, serverId)

        return True
    
    def delete(self, username):
        # delete all domains
        if os.path.exists(get_root_dir() + 'data/' + username) and os.path.exists(get_root_dir() + 'data/' + username + '/domains'):
            domainLines = os.listdir(get_root_dir() + 'data/' + username + '/domains')

            for domainLine in domainLines:
                domainname = domainLine.strip("\n")
                domain = Domain()
                domain.delete(username, domainname)

        delete_user(username)

        return True
    
    def update(self, username, disk_usage=None, cpu_limit=None, ram_limit=None, disk_limit=None):
        # read user config file
        with open(get_root_dir() + 'data/' + username + '/user.conf') as file:
            userJson = json.load(file)

        # update user config file
        if disk_usage:
            userJson['disk_usage'] = disk_usage
        if cpu_limit:
            userJson['cpu_limit'] = cpu_limit
        if ram_limit:
            userJson['ram_limit'] = ram_limit
        if disk_limit:
            userJson['disk_limit'] = disk_limit

        with open(get_root_dir() + 'data/' + username + '/user.conf', 'w') as file:
            json.dump(userJson, file)

        return True

class UserExistsError(Exception):
    pass
