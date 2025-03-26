from .model import Model
import json
import os

from tpweb.func.domain import do_domain_exists, create_domain_filesystem, create_domain_config, delete_domain, do_template_exists, install_template
from tpweb.func.user import do_user_exists, get_server_id
from tpweb.func.server import get_haproxy_server_id
from tpweb.func.haproxy import createHost

from tpweb.config import get_root_dir

class Domain(Model):
    name = 'domain'
    path = 'domain'

    def list(self):
        # open file and list all users
        file = get_root_dir() + 'data/domains.conf'

        # read file line by line
        with open(file, 'r') as file:
            lines = file.readlines()

        domains = []
        for line in lines:
            line = line.strip("\n")

            id = line.split(":")[0]
            username = line.split(":")[1]
            domainname = line.split(":")[2]

            with open(get_root_dir() + 'data/' + username + '/' + domainname + '/domain.conf') as file:
                domainData = json.load(file)

            domains.append({domainname: domainData})

        return domains

    def get(self, domainname):
        # read domains.conf file and check if domain exists
        with open(get_root_dir() + 'data/domains.conf', 'r') as file:
            domainLines = file.readlines()

        username=None
        for domainLine in domainLines:
            domainLine = domainLine.strip("\n")
            # if line ends with :domainname
            if domainLine.endswith(":" + domainname):
                username = domainLine.split(":")[1]
                break

        if username == None:
            raise DomainDoesNotExistError('Domain does not exist')
        
        if os.path.exists(get_root_dir() + 'data/' + username + '/' + domainname + '/domain.conf') == False:
            raise DomainDoesNotExistError('Domain does not exist')

        with open(get_root_dir() + 'data/' + username + '/' + domainname + '/domain.conf') as file:
            domainnameJson = json.load(file)

        return domainnameJson

    def create(self, username, domainname, Web=True, DNS=True, Mail=True, webTemplate=None, dnsTemplate=None):
        # check if user already exists on linux system

        if(do_user_exists(username) == False):
            raise UserDoesNotExistError('User does not exist')
        
        if(do_domain_exists(domainname) == True):
            raise DomainExistsError('Domain already exists')
        
        if webTemplate and not do_template_exists(webTemplate):
            raise Exception('Web template does not exist')
        
        if webTemplate == None:
            webTemplate = 'client'

        serverId = get_server_id(username)

        create_domain_filesystem(username, domainname, Web=Web, DNS=DNS, Mail=Mail, serverId=serverId)

        create_domain_config(username, domainname, Web=Web, DNS=DNS, Mail=Mail, webTemplate=webTemplate, dnsTemplate=dnsTemplate, serverId=serverId)

        #install_template(username, domainname, webTemplate, serverId)

        haproxyServerId = serverId #get_haproxy_server_id(serverId)
        createHost(domainname, haproxyServerId)
        return True
    
    def delete(self, username, domainname):
        if(do_domain_exists(domainname) == True):
            delete_domain(username, domainname)

        return True
    
    def update(self, username, domainname, disk_usage=None, cpu_limit=None, ram_limit=None, disk_limit=None, proxy_id=None):
        # read user config file
        with open(get_root_dir() + 'data/' + username + '/' + domainname + '/domain.conf') as file:
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
        if proxy_id:
            userJson['proxy_id'] = proxy_id

        # write user config file
        with open(get_root_dir() + 'data/' + username + '/' + domainname + '/domain.conf', 'w') as file:
            json.dump(userJson, file)

        return True

class UserDoesNotExistError(Exception):
    pass

class DomainDoesNotExistError(Exception):
    pass

class DomainExistsError(Exception):
    pass