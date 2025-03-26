import pwd
import subprocess
from subprocess import check_output
import json
from tpweb.config import get_root_dir, get_config
import re
import os
import datetime
from tpweb.func.server import get_server_type
from tpweb.func.user import get_server_id

def is_valid_domain(domainname):
    # check if domainname is valid (regex)
    regex='^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}$'
    if re.match(regex, domainname):
        return True
    return False

def do_domain_exists(domainname):
    # check if domain already exists
    from tpweb.data.domain import Domain, DomainDoesNotExistError
    domain = Domain()
    try :
        if(domain.get(domainname)):
            return True
    except DomainDoesNotExistError:
        return False
    
    return False

def get_next_id():
    with open(get_root_dir() + 'data/domains.conf', 'r') as file:
        lines = file.readlines()

    if len(lines) == 0:
        return 10
    
    lastLine = lines[-1]
    lastId = int(lastLine.split(":")[0])

    return lastId + 1

def do_template_exists(template):
    # check if template exists
    dirname = get_root_dir() + 'templates/' + template
    if os.path.isdir(dirname):
        return True
    return False

def create_domain_filesystem(username, domainname, Web=True, DNS=True, Mail=True, serverId=None):
    serverType = get_server_type(serverId)
    if(serverType == 'main'):
        create_domain_filesystem_main(username, domainname, Web, DNS, Mail)
    else:
        create_domain_filesystem_remote(username, domainname, serverId, Web, DNS, Mail)

    # create directorie data/$username in this python project
    #output = subprocess.run(['mkdir', get_root_dir() + 'data/' + username + '/' + domainname])

def create_domain_filesystem_remote(username, domainname, serverId, Web=True, DNS=True, Mail=True):
    raise Exception('Not implemented')

def create_domain_filesystem_main(username, domainname, Web=True, DNS=True, Mail=True):
    # create default directories
    docroot = '/var/www/html/' + domainname
    
    #Create docroot directory
    output = subprocess.run(['docker', '--context', username, 'compose', '-f', '/home/' + username + '/docker-compose.yml', 'run', '--rm', '-v', username + '_html_data:/var/www/html/', 'busybox', 'sh', '-c', 'mkdir -p ' + docroot + ' && chown 0:33 ' + docroot + ' && chmod -R g+w ' + docroot])
    if output.returncode != 0:
        raise Exception('Failed to create directories')
    
    #Nginx config
    #Check if the nginx config file exists
    if os.path.exists('/home/' + username + '/nginx.conf') == False:

        #Create default nginx config file
        with open('/home/' + username + '/nginx.conf', 'w') as file:
            file.write('user  nginx;')
            file.write('worker_processes  auto;')
            file.write('pid        /var/run/nginx.pid;')
            file.write('events {')
            file.write('    worker_connections  1024;')
            file.write('}')
            file.write('http {')
            file.write('    include       /etc/nginx/mime.types;')
            file.write('    default_type  application/octet-stream;')
            file.write('    sendfile        on;')
            file.write('    keepalive_timeout  65;')
            file.write('    include /etc/nginx/conf.d/*.conf;')
            file.write('}')
    
    #vhost_in_docker_file="/etc/$ws/conf.d/${domain_name}.conf" 		
    templatepath = get_root_dir() + 'templates/client/nginx-vhost.conf'
    dockerVhost="/home/" + username + "/docker-data/volumes/" + username + "_webserver_data/_data/" + domainname + ".conf"
    #Copy the nginx config file to the docker volume
    output = subprocess.run(['cp', templatepath, dockerVhost])
    if output.returncode != 0:
        raise Exception('Failed to copy nginx config file')
    
    #Change the nginx config file
    with open(dockerVhost, 'r') as file:
        content = file.read()
    content = content.replace('<DOMAIN_NAME>', domainname)
    content = content.replace('<USER>', username)
    content = content.replace('<PHP>', '8.3')
    content = content.replace('<DOCUMENT_ROOT>', docroot)
    with open(dockerVhost, 'w') as file:
        file.write(content)


    #Apache
    #templatepath = get_root_dir() + 'templates/client/apache-vhost.conf'
    #dockerVhost="/home/" + username + "/docker-data/volumes/" + username + "_webserver_data/_data/" + domainname + ".conf"
    #Copy the apache config file to the docker volume
    #output = subprocess.run(['cp', templatepath, dockerVhost])
    #if output.returncode != 0:
    #    raise Exception('Failed to copy apache config file')

    #start the webserver
    webserver='nginx'
    #docker --context $context compose -f /home/$username/docker-compose.yml up -d $webserver > /dev/null 2>&1

    #Check if the webserver is already running
    output = subprocess.run(['docker', '--context', username, 'compose', '-f', '/home/' + username + '/docker-compose.yml', 'ps', '-q', webserver], stdout=subprocess.PIPE)
    if output.returncode == 0:
        #Stop the webserver
        output = subprocess.run(['docker', '--context', username, 'compose', '-f', '/home/' + username + '/docker-compose.yml', 'down', webserver])

    #Start the webserver
    output = subprocess.run(['docker', '--context', username, 'compose', '-f', '/home/' + username + '/docker-compose.yml', 'up', '-d', webserver])
    if output.returncode != 0:
        raise Exception('Failed to start webserver')
    
    #Start PHP
    #docker --context $context compose -f /home/$username/docker-compose.yml up -d php-fpm-8.3 > /dev/null 2>&1
    #Check if PHP is already running
    output = subprocess.run(['docker', '--context', username, 'compose', '-f', '/home/' + username + '/docker-compose.yml', 'ps', '-q', 'php-fpm-8.3'], stdout=subprocess.PIPE)
    if output.returncode == 0:
        #Stop PHP
        output = subprocess.run(['docker', '--context', username, 'compose', '-f', '/home/' + username + '/docker-compose.yml', 'down', 'php-fpm-8.3'])

    #Start PHP
    output = subprocess.run(['docker', '--context', username, 'compose', '-f', '/home/' + username + '/docker-compose.yml', 'up', '-d', 'php-fpm-8.3'])
    if output.returncode != 0:
        raise Exception('Failed to start PHP')



def create_domain_config(username, domainname, Web=True, DNS=True, Mail=True, webTemplate=None, dnsTemplate=None, serverId=None):
    # check if folder exists
    output = subprocess.run(['mkdir', get_root_dir() + 'data/' + username + '/' + domainname])
    if output.returncode != 0:
        raise Exception('Failed to create directories')
    
    # create config files
    output = subprocess.run(['touch', get_root_dir() + 'data/' + username + '/' + domainname + '/domain.conf'])
    if output.returncode != 0:
        raise Exception('Failed to create config files')

    output = subprocess.run(['touch', get_root_dir() + 'data/' + username + '/' + domainname + '/dns.conf'])
    if output.returncode != 0:
        raise Exception('Failed to create config files')
        
    output = subprocess.run(['touch', get_root_dir() + 'data/' + username + '/' + domainname + '/mail.conf'])
    if output.returncode != 0:
        raise Exception('Failed to create config files')
    
    id = get_next_id()

    #append user to file
    with open(get_root_dir() + 'data/domains.conf', 'a') as file:
        file.write(str(id) + ":" + str(username) + ':' + domainname + '\n')

    domain = {
        'id': id,
        'username': username,
        'domainname': domainname,
        'server_id': serverId,
        'web': Web,
        'dns': DNS,
        'mail': Mail,
        'ipv4': None,
        'ipv6': None,
        'template': webTemplate,
        'dns_template': dnsTemplate,
        'proxy_id': None,
        'dns_id': None,
        'disk_usage': 0,
        'cpu_limit': 2,
        'ram_limit': 2000,
        'disk_limit': 10000
    }

    if DNS:
        dnsRecords = []
        dnsRecords.append({'type': 'A', 'name': '@', 'value': get_config()['IPV4']})
        dnsRecords.append({'type': 'A', 'name': 'www', 'value': get_config()['IPV4']})
        dnsRecords.append({'type': 'A', 'name': 'mail', 'value': get_config()['IPV4']})

        dnsRecords.append({'type': 'MX', 'name': '@', 'value': 'mail.' + domainname})
        spf = "ip4:" + get_config()['IPV4']
        

        if get_config()['IPV6']:
            dnsRecords.append({'type': 'AAAA', 'name': '@', 'value': get_config()['IPV6']})
            dnsRecords.append({'type': 'AAAA', 'name': 'www', 'value': get_config()['IPV6']})
            dnsRecords.append({'type': 'AAAA', 'name': 'mail', 'value': get_config()['IPV6']})
            spf += " ip6:" + get_config()['IPV6']

        dnsRecords.append({'type': 'TXT', 'name': '@', 'value': '"v=spf1 a mx ' + spf + ' -all"'})
        dnsRecords.append({'type': 'TXT', 'name': '_dmarc', 'value': '"v=DMARC1; p=none; rua=mailto:dmarc@ech.be; ruf=mailto:dmarc@ech.be; fo=1;'})

        with open(get_root_dir() + 'data/' + username + '/' + domainname + '/dns.conf', 'w') as file:
            json.dump(dnsRecords, file)

    # write user config file
    with open(get_root_dir() + 'data/' + username + '/' + domainname + '/domain.conf', 'w') as file:
        json.dump(domain, file)

    serverType = get_server_type(serverId)
    if(serverType == 'worker'):
        # send domain to worker
        sync_domain_to_worker(username, domainname)

def sync_domain_to_worker(username, domainname):
    raise Exception('Not implemented')

def install_template(username, domainname, template, serverId):
    serverType=get_server_type(serverId)
    if(serverType == 'main'):
        install_template_main(username, domainname, template, serverId)
    else:
        install_template_remote(username, domainname, template, serverId)
    
def install_template_remote(username, domainname, template, serverId):
    raise Exception('Not implemented')

def install_template_main(username, domainname, template, serverId):
    # remove current template
    stop_domain(username, domainname, serverId)

    from tpweb.data.domain import Domain
    domainInfo = Domain().get(domainname)

    date=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    #create backup folder
    output = subprocess.run(['mkdir', '/home/' + username + '/data/' + domainname + '/config-' + date])

    # move config files to backup location
    output = subprocess.run(['mv', '/home/' + username + '/data/' + domainname + '/config/*', '/home/' + username + '/data/' + domainname + '/config-' + date], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    output = subprocess.run(['mv', '/home/' + username + '/data/' + domainname + '/docker-compose.yml', '/home/' + username + '/data/' + domainname + '/config-' + date], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    output = subprocess.run(['cp', '-rf', get_root_dir() + 'templates/' + template + '/config', '/home/' + username + '/data/' + domainname + '/'])
    if output.returncode != 0:
        raise Exception('Failed to install template')
    output = subprocess.run(['cp', '-rf', get_root_dir() + 'templates/' + template + '/docker-compose.yml', '/home/' + username + '/data/' + domainname + '/'])
    if output.returncode != 0:
        raise Exception('Failed to install template')

    domainnameStr=domainname.replace(".", "-")
    id=str(domainInfo['id'])
    # make id always 3 digits
    if len(id) == 1:
        id = '00' + id
    elif len(id) == 2:
        id = '0' + id
    
    # open each file in the template folder and replace the variables
    for root, dirs, files in os.walk('/home/' + username + '/data/' + domainname + '/config'):
        for file in files:
            with open(os.path.join(root, file), 'r') as f:
                content = f.read()
            content = content.replace('#domainstr#', domainnameStr)
            content = content.replace('#username#', username)
            content = content.replace('#userid#', str(pwd.getpwnam(username).pw_uid))
            content = content.replace('#domainname#', domainname)
            content = content.replace('#ID#', id)
            with open(os.path.join(root, file), 'w') as f:
                f.write(content)
    
    # replace variables in docker-compose.yml
    with open('/home/' + username + '/data/' + domainname + '/docker-compose.yml', 'r') as f:
        content = f.read()

    content = content.replace('#domainstr#', domainnameStr)
    content = content.replace('#username#', username)
    content = content.replace('#userid#', str(pwd.getpwnam(username).pw_uid))
    content = content.replace('#domainname#', domainname)
    content = content.replace('#ID#', id)
    with open('/home/' + username + '/data/' + domainname + '/docker-compose.yml', 'w') as f:
        f.write(content)

    # chown directories
    output = subprocess.run(['chown', '-R', username + ':' + username, '/home/' + username + '/data/' + domainname + '/config'])
    if output.returncode != 0:
        raise Exception('Failed to chown directories')
    
    output = subprocess.run(['chown', '-R', username + ':' + username, '/home/' + username + '/data/' + domainname + '/docker-compose.yml'])
    if output.returncode != 0:
        raise Exception('Failed to chown directories')
    
    start_domain(username, domainname, serverId)

def stop_domain(username, domainname, serverId):
    serverType=get_server_type(serverId)
    if(serverType == 'main'):
        # login as user and stop docker compose
        subprocess.run(['su', username, '-c', 'docker compose -f /home/' + username + '/data/' + domainname + '/docker-compose.yml down'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        stop_domain_remote(username, domainname, serverId)

def stop_domain_remote(username, domainname, serverId):
    raise Exception('Not implemented')

def start_domain(username, domainname, serverId):
    serverType=get_server_type(serverId)
    if(serverType == 'main'):
        # login as user and start docker compose
        subprocess.run(['su', username, '-c', 'docker compose -f /home/' + username + '/data/' + domainname + '/docker-compose.yml up -d'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        start_domain_remote(username, domainname, serverId)

def start_domain_remote(username, domainname, serverId):
    raise Exception('Not implemented')

def delete_domain(username, domainname):
    serverId=get_server_id(username)
    serverType=get_server_type(serverId)

    if(serverType == 'main'):
        delete_domain_main(username, domainname, serverId)
    else:
        delete_domain_remote(username, domainname, serverId)

    # remove domain from haproxy
    from tpweb.func.haproxy import deleteHost
    deleteHost(domainname)

    # delete domain from domains.conf
    with open(get_root_dir() + 'data/domains.conf', 'r') as file:
        lines = file.readlines()
    with open(get_root_dir() + 'data/domains.conf', 'w') as file:
        for line in lines:
            if line.strip("\n").split(":")[2] != domainname:
                file.write(line)
    
    # delete domain config directory
    output = subprocess.run(['rm', '-r', get_root_dir() + 'data/' + username + '/' + domainname])
    if output.returncode != 0:
        raise Exception('Failed to delete domain')

    # Todo: recalculate disk usage from user

def delete_domain_remote(username, domainname, serverId):
    raise Exception('Not implemented')

def delete_domain_main(username, domainname, serverId):
    # stop domain
    stop_domain(username, domainname, serverId)

    # delete user from this python project
    output = subprocess.run(['rm', '-r', "/home/" + username + "/data/" + domainname])
    if output.returncode != 0:
        raise Exception('Failed to delete domain')

def calculate_disk_usage(username, domainname):
    serverId = get_server_id(username)
    serverType = get_server_type(serverId)
    
    if(serverType == 'main'):
        # calculate disk usage
        output = check_output(['du', '-s', '/home/' + username + '/data/' + domainname])
        return int(output.split()[0].decode('utf-8'))
    else:
        return 0

def create_folder(folder):
    # create folder
    output = subprocess.run(['mkdir', '-p', folder])
    if output.returncode != 0:
        raise Exception('Failed to create folder: ' + folder)