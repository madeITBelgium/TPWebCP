#!/bin/bash

# This script is used to install TPWeb CP on a fresh Almalinux 9 system
VERSION="0.0.1"
INSTALLDIR="/usr/local/tpwebcp"

# Check if this server is running Almalinux 9
if [ ! -f /etc/almalinux-release ]; then
    echo "This script is only for Almalinux 9"
    exit 1
fi

# Check if the user is root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 2
fi

# Install yum-utils
sudo yum install -y yum-utils wget python3 python3-pip git bc fuse-overlayfs systemd-container > /dev/null

# Install docker
# Check if docker is already installed
if [ -x "$(command -v docker)" ]; then
    echo "Docker is already installed."
else
    echo "Installing Docker ..."

    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    sudo groupadd docker

    sudo systemctl disable --now docker.service docker.socket
    sudo rm /var/run/docker.sock

    sudo modprobe ip_tables

    mkdir -p /etc/systemd/system/user@.service.d

    cat > /etc/systemd/system/user@.service.d/delegate.conf << EOF
[Service]
Delegate=cpu cpuset io memory pids
EOF

    systemctl daemon-reload
    systemctl enable --now docker
    systemctl start docker
fi

# Install tpweb
git clone https://github.com/madeITBelgium/TPWebCP.git $INSTALLDIR
cd $INSTALLDIR/tpweb

# pip3 install requirements as root
pip3 install -r requirements.txt

# Install config
mkdir -p /etc/tpwebcp/caddy /etc/tpwebcp/caddy/ssl /etc/tpwebcp/caddy/domains /etc/tpwebcp/bind

# Install templates
cp $INSTALLDIR/templates/server/.env.template /root/.env
cp $INSTALLDIR/templates/server/docker-compose.yml /root/docker-compose.yml
cp $INSTALLDIR/templates/server/config/caddy/* /etc/tpwebcp/caddy/

wget https://raw.githubusercontent.com/corazawaf/coraza/v3/dev/coraza.conf-recommended -O /etc/tpwebcp/caddy/coraza_rules.conf
git clone https://github.com/coreruleset/coreruleset /etc/tpwebcp/caddy/coreruleset/

cp $INSTALLDIR/templates/server/config/bind/* /etc/tpwebcp/bind/

docker --context default run --rm \
    -v /etc/tpwebcp/bind/:/etc/bind/ \
    --entrypoint=/bin/sh \
    ubuntu/bind9:latest \
    -c 'rndc-confgen -a -A hmac-sha256 -b 256 -c /etc/bind/rndc.key'

find /etc/tpwebcp/bind/ -type d -print0 | xargs -0 chmod 755
find /etc/tpwebcp/bind/ -type f -print0 | xargs -0 chmod 644

# Start docker container
cd /root
docker compose up -d

# Add $INSTALLDIR to PATH of root user
echo "export PATH=\$PATH:$INSTALLDIR" >> /root/.bashrc

# Ask if current hostname is correct or not
echo "Current hostname is $(hostname)"
read -p "Is this hostname correct? [y/n]: " -n 1 -r
echo   # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Hostname is $(hostname)"
else
    read -p "Enter the correct hostname: " NEWHOSTNAME
    hostnamectl set-hostname $NEWHOSTNAME
    echo "Hostname changed to $NEWHOSTNAME"
fi

$INSTALLDIR/tpweb-bin init --main

exit 0

# Check if HAProxy is already installed by checking if $INSTALLDIR/haproxy exists
if [ -d "$INSTALLDIR/haproxy" ]; then
    echo "HAProxy is already installed."
else
    # Ask if you wanna use this server as load balancer or not
    read -p "Do you want to use this server as a load balancer? (Default: y) [y/n]: " -n 1 -r
    echo   # (optional) move to a new line
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Skip load balancer installation"
    else
        # Install HAProxy
        mkdir -p $INSTALLDIR/haproxy

        # Create docker-compose.yml
        echo "version: '3.8'" > $INSTALLDIR/haproxy/docker-compose.yml
        echo "services:" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "  haproxy:" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "    image: 'jc21/nginx-proxy-manager:latest'" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "    restart: unless-stopped" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "    ports:" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "      - '80:80'" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "      - '443:443'" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "      - '81:81'" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "      - '21:21'" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "    volumes:" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "      - ./data:/data" >> $INSTALLDIR/haproxy/docker-compose.yml
        echo "      - ./letsencrypt:/etc/letsencrypt" >> $INSTALLDIR/haproxy/docker-compose.yml

        # Create data folder
        mkdir -p $INSTALLDIR/haproxy/data
        mkdir -p $INSTALLDIR/haproxy/letsencrypt

        # Start HAProxy
        cd $INSTALLDIR/haproxy
        docker compose up -d
        cd $INSTALLDIR
    fi
fi

# Check if PowerDNS is already installed by checking if $INSTALLDIR/powerdns exists
if [ -d "$INSTALLDIR/powerdns" ]; then
    echo "PowerDNS is already installed."
else
    # Ask if you wanna use this server as a dns nameserver
    read -p "Do you want to use this server as a DNS nameserver? (Default: y) [y/n]: " -n 1 -r
    echo   # (optional) move to a new line
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Skip DNS nameserver installation"
    else
        # Install PowerDNS
        mkdir -p $INSTALLDIR/powerdns

        # generate random password
        PDNS_PASSWORD=$(openssl rand -base64 12)
        APIKEY=$(openssl rand -base64 24)

        echo "$PDNS_PASSWORD" > $INSTALLDIR/powerdns/pdns_db_password
        echo "$APIKEY" > $INSTALLDIR/powerdns/pdns_api_key

        echo "services:" > $INSTALLDIR/powerdns/docker-compose.yml
        echo "  db:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    image: mariadb:latest" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    environment:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - MYSQL_ALLOW_EMPTY_PASSWORD=yes" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - MYSQL_DATABASE=powerdnsadmin" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - MYSQL_USER=pdns " >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - MYSQL_PASSWORD=$PDNS_PASSWORD" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    restart: always" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    volumes:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - ./pda-mysql:/var/lib/mysql" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "  pdns:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    image: pschiffe/pdns-mysql" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    hostname: pdns" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    domainname: $(hostname)" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    restart: always" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    depends_on:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - db" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    links:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - "db:mysql"" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    ports:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - "53:53"" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - "53:53/udp"" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - "8081:8081"" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "    environment:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_gmysql_host=db" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_gmysql_port=3306" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_gmysql_user=pdns" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_gmysql_dbname=powerdnsadmin" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_gmysql_password=$PDNS_PASSWORD" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_master=yes " >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_api=yes" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_api_key=$APIKEY" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNSCONF_API_KEY=$APIKEY" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_webserver=yes" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_webserver-allow-from=0.0.0.0/0" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_webserver_address=0.0.0.0" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_version_string=anonymous" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_default_ttl=900" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - PDNS_allow_notify_from=20.218.124.145" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - PDNS_allow_axfr_ips=20.218.124.145" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - PDNS_only_notify=20.218.124.145" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_gmysql_dnssec=yes" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "      - PDNS_default_soa_content=$(hostname) hostmaster.@ 0 10800 3600 604800 3600" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#  web_app:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    image: powerdnsadmin/pda-legacy:latest" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    container_name: powerdns_admin" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    ports:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - "8989:80"" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    depends_on:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - db" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    restart: always" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    links:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - db:mysql" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - pdns:pdns" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    logging:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      driver: json-file" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      options:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#        max-size: 50m" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#    environment:" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - SQLALCHEMY_DATABASE_URI=mysql://pdns:$PDNS_PASSWORD@db/powerdnsadmin" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - GUNICORN_TIMEOUT=60" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - GUNICORN_WORKERS=2" >> $INSTALLDIR/powerdns/docker-compose.yml
        echo "#      - GUNICORN_LOGLEVEL=DEBUG" >> $INSTALLDIR/powerdns/docker-compose.yml

        cd $INSTALLDIR/powerdns
        docker compose up -d
        cd $INSTALLDIR
    fi
fi

# Install tpweb

# Check script parameters --main or --worker
if [ "$1" == "--worker" ]; then
    # Install worker node
    echo "Installing worker node"
    #./tpweb-bin init --worker
else
    # Install main node
    echo "Installing main node"
    #./tpweb-bin init --main
fi