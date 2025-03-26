import requests
import os
import json
import subprocess
from tpweb.func.server import get_server

from tpweb.config import get_root_dir

def createHost(domainname, serverId):
    from tpweb.data.domain import Domain
    from tpweb.data.user import User
    domain = Domain()
    domainData = domain.get(domainname)
    id=domainData['id']

    user = User()
    userData = user.get(domainData['username'])
    #print(userData)
    portprefix = userData['portprefix']

    templetfile = get_root_dir() + 'templates/client/config/caddy/template.conf'
    
    #Copy the template file to the domain directory /etc/tpwebcp/caddy/domains/{domainname}.conf
    domainFile = '/etc/tpwebcp/caddy/domains/' + domainname + '.conf'

    with open(templetfile, 'r') as file:
        template = file.read()

    template = template.replace("<DOMAIN_NAME>", domainname)
    template = template.replace("<NON_SSL_PORT>", portprefix + '5')
    template = template.replace("<SSL_PORT>", portprefix + '6')

    with open(domainFile, 'w') as file:
        file.write(template)

    #Restart caddy server
    #docker exec caddy caddy reload --config /etc/caddy/Caddyfile
    output = subprocess.run(["docker", "exec", "caddy", "caddy", "reload", "--config", "/etc/caddy/Caddyfile", ">", "/dev/null"], stdout=subprocess.PIPE)
    if output.returncode != 0:
        raise Exception('Failed to reload caddy server')


def deleteHost(domainname):
    domainFile = '/etc/tpwebcp/caddy/domains/' + domainname + '.conf'

    if os.path.exists(domainFile):
        os.remove(domainFile)

    #Restart caddy server
    #docker exec caddy caddy reload --config /etc/caddy/Caddyfile
    output = subprocess.run(["docker", "exec", "caddy", "caddy", "reload", "--config", "/etc/caddy/Caddyfile"], stdout=subprocess.PIPE)
    if output.returncode != 0:
        raise Exception('Failed to reload caddy server')
