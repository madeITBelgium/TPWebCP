#!/bin/bash

# Controleer of het script met drie argumenten is aangeroepen
if [ "$#" -ne 3 ]; then
    echo "Gebruik: $0 <Username> <Password> <TemplatePath>"
    exit 1
fi

USERNAME=$1
PASSWORD=$2
TEMPLATE_PATH=$3
USER_HOME="/home/$USERNAME"
DOCKER_COMPOSE_FILE="$USER_HOME/docker-compose.yml"
DOCKER_CONTEXT_NAME="${USERNAME}"
DISK_LIMIT="10G"
INODE_LIMIT="100000"

# Controleer of de gebruiker bestaat en verwijder alles indien nodig
if id "$USERNAME" &>/dev/null; then
    echo "Gebruiker $USERNAME bestaat al. Verwijderen..."
    killall -u $USERNAME -9  > /dev/null 2>&1
    docker context rm "$DOCKER_CONTEXT_NAME" 2>/dev/null
    systemctl stop "docker@$USERNAME" 2>/dev/null
    userdel "$USERNAME" --force --remove 2>/dev/null
    rm -rf "/home/$USERNAME"
fi

# Voeg de gebruiker toe
echo "Gebruiker $USERNAME aanmaken..."
adduser --home "$USER_HOME" --shell /bin/bash "$USERNAME" > /dev/null 2>&1
echo "$USERNAME:$PASSWORD" | chpasswd

# Get userID
userID=$(id -u $USERNAME 2>/dev/null)

# Controleer of de gebruiker correct is aangemaakt
if ! id "$USERNAME" &>/dev/null; then
    echo "❌ Fout bij aanmaken van gebruiker $USERNAME"
    exit 1
fi

echo "✅ Gebruiker $USERNAME is correct aangemaakt."


portprefix=$userID
#Make sure the port prefix is 4 digits, when it is less than 4 digits, add 0s to the front but starts with 1
if [ ${#portprefix} -lt 4 ]; then
    portprefix=$(printf "%04d" $portprefix)
fi

# Add +1 to the first digit of the port prefix
portprefix=$(echo $portprefix | sed 's/^\(.\)/\1+1/' | bc)

echo "Port prefix: $portprefix"

# Installeer Docker rootless voor de gebruiker
echo "Docker rootless installeren voor $USERNAME..."
mkdir -p /home/$USERNAME/docker-data /home/$USERNAME/.config/docker > /dev/null 2>&1
		
echo "{
	\"data-root\": \"/home/$USERNAME/docker-data\",
    \"no-new-privileges\": true
}" > /home/$USERNAME/.config/docker/daemon.json

mkdir -p /home/$USERNAME/bin > /dev/null 2>&1
chmod 755 -R /home/$USERNAME/ >/dev/null 2>&1
sed -i '1i export PATH=/home/'"$USERNAME"'/bin:$PATH' /home/"$USERNAME"/.bashrc


loginctl enable-linger $USERNAME >/dev/null 2>&1
mkdir -p /home/$USERNAME/.docker/run /home/$USERNAME/bin/ /home/$USERNAME/bin/.config/systemd/user/ >/dev/null 2>&1
chmod 700 /home/$USERNAME/.docker/run >/dev/null 2>&1
chmod 755 -R /home/$USERNAME/ >/dev/null 2>&1
chown -R $USERNAME:$USERNAME /home/$USERNAME/ >/dev/null 2>&1

system_wide_rootless_script="$TEMPLATE_PATH/docker/dockerd-rootless-setuptool.sh"
if [ ! -f "$system_wide_rootless_script" ]; then
	curl -sSL https://get.docker.com/rootless -o $system_wide_rootless_script
   chmod +x $system_wide_rootless_script
fi

ln -sf $system_wide_rootless_script /home/$USERNAME/bin/dockerd-rootless-setuptool.sh

machinectl shell $USERNAME@ /bin/bash -c "
    # Setup environment for rootless Docker
    source ~/.bashrc

    /home/$USERNAME/bin/dockerd-rootless-setuptool.sh install >/dev/null 2>&1

    echo 'export XDG_RUNTIME_DIR=/home/$USERNAME/.docker/run' >> ~/.bashrc
    echo 'export PATH=/home/$USERNAME/bin:\$PATH' >> ~/.bashrc
    echo 'export DOCKER_HOST=unix:///run/user/$userID/docker.sock' >> ~/.bashrc

    source ~/.bashrc
    mkdir -p ~/.config/systemd/user/

    cat <<EOF > ~/.config/systemd/user/docker.service
[Unit]
Description=Docker Application Container Engine (Rootless)
After=network.target

[Service]
Environment=PATH=/home/$USERNAME/bin:\$PATH
Environment=DOCKER_HOST=unix:///run/user/$userID/docker.sock
ExecStart=/home/$USERNAME/bin/dockerd-rootless.sh
Restart=on-failure
StartLimitBurst=3
StartLimitInterval=60s

[Install]
WantedBy=default.target
EOF

    systemctl --user daemon-reload
    systemctl --user restart docker
"


echo "Docker rootless installatie voltooid!"

docker context create $USERNAME \
    --docker "host=unix:///run/user/$userID/docker.sock" \
    --description "$USERNAME"


echo "Docker rootless installatie afgerond voor ${USERNAME}."

# Controleer of Docker correct draait
sleep 5
if ! sudo -u "$USERNAME" -- sh -c "docker info"; then
    echo "❌ Fout: Docker rootless is niet correct gestart voor $USERNAME."
    exit 1
fi

echo "✅ Docker rootless is correct gestart."

# Kopieer de Docker Compose-template
echo "Kopiëren van Docker Compose-template..."
sudo cp "$TEMPLATE_PATH/templates/client/docker-compose.yml" "$DOCKER_COMPOSE_FILE"
sudo chown "$USERNAME:$USERNAME" "$DOCKER_COMPOSE_FILE"



# Ports
port_1="${portprefix}1:22"
port_2="${portprefix}2:3306"
port_3="${portprefix}3:7681"
port_4="${portprefix}4:80"
port_5="${portprefix}5:80"
port_6="${portprefix}6:443"
port_7="${portprefix}7:80"
port_8="${portprefix}8:80"
port_9="${portprefix}9:5432"
cpu="4"
ram="2g"
hostname="$USERNAME.tpweb.dev"
postgres_password=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')
mysql_root_password=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')
pg_admin_password=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')
default_php_version="8.4"
email="info@$USERNAME.tpweb.dev"

cp $TEMPLATE_PATH/templates/client/.env.template /home/$USERNAME/.env

sed -i -e "s|USERNAME=\"[^\"]*\"|USERNAME=\"$USERNAME\"|g" \
    -e "s|USER_ID=\"[^\"]*\"|USER_ID=\"$userID\"|g" \
    -e "s|CONTEXT=\"[^\"]*\"|CONTEXT=\"$USERNAME\"|g" \
    -e "s|TOTAL_CPU=\"[^\"]*\"|TOTAL_CPU=\"$cpu\"|g" \
    -e "s|TOTAL_RAM=\"[^\"]*\"|TOTAL_RAM=\"$ram\"|g" \
    -e "s|^HTTP_PORT=\"[^\"]*\"|HTTP_PORT=\"$port_5\"|g" \
    -e "s|HTTPS_PORT=\"[^\"]*\"|HTTPS_PORT=\"$port_6\"|g" \
    -e "s|HOSTNAME=\"[^\"]*\"|HOSTNAME=\"$hostname\"|g" \
    -e "s|SSH_PORT=\"[^\"]*\"|SSH_PORT=\"127.0.0.1:$port_1\"|g" \
    -e "s|TTYD_PORT=\"[^\"]*\"|TTYD_PORT=\"$port_3\"|g" \
    -e "s|PMA_PORT=\"[^\"]*\"|PMA_PORT=\"$port_4\"|g" \
    -e "s|POSTGRES_PASSWORD=\"[^\"]*\"|POSTGRES_PASSWORD=\"$postgres_password\"|g" \
    -e "s|PGADMIN_PW=\"[^\"]*\"|PGADMIN_PW=\"$pg_admin_password\"|g" \
    -e "s|PGADMIN_MAIL=\"[^\"]*\"|PGADMIN_MAIL=\"$email\"|g" \
    -e "s|MYSQL_PORT=\"[^\"]*\"|MYSQL_PORT=\"127.0.0.1:$port_2\"|g" \
    -e "s|DEFAULT_PHP_VERSION=\"[^\"]*\"|DEFAULT_PHP_VERSION=\"$default_php_version\"|g" \
    -e "s|MYSQL_ROOT_PASSWORD=\"[^\"]*\"|MYSQL_ROOT_PASSWORD=\"$mysql_root_password\"|g" \
    -e "s|PROXY_HTTP_PORT=\"[^\"]*\"|#PROXY_HTTP_PORT=\"$port_7\"|g" \
    -e "s|PGADMIN_PORT=\"[^\"]*\"|PGADMIN_PORT=\"$port_8\"|g" \
    -e "s|POSTGRES_PORT=\"[^\"]*\"|POSTGRES_PORT=\"$port_9\"|g" \
    -e "s|MSSQL_PORT==\"[^\"]*\"|MSSQL_PORT==\"$port_9\"|g" \
    "/home/$USERNAME/.env"


mkdir -p /home/$USERNAME/sockets/{mysqld,postgres,redis,memcached}
echo "[mysqld]" > /home/$USERNAME/custom.cnf
cp $TEMPLATE_PATH/templates/client/nginx.conf /home/$USERNAME/nginx.conf
cp $TEMPLATE_PATH/templates/client/httpd.conf /home/$USERNAME/httpd.conf
cp $TEMPLATE_PATH/templates/client/varnish.conf /home/$USERNAME/default.vcl
mkdir -p /home/$USERNAME/php.ini
cp $TEMPLATE_PATH/templates/client/php/* /home/$USERNAME/php.ini/
chown -R $USERNAME:$USERNAME /home/$USERNAME
chmod 777 /home/$USERNAME/sockets/

echo "[client]
user=root
password="$mysql_root_password"
" > /home/$USERNAME/my.cnf

chown -R $USERNAME:$USERNAME /home/$USERNAME

# Start de Docker container met opslag- en inode-limieten
echo "Starten van Docker Compose $USERNAME container..."
sudo -u "$USERNAME" sh -c "docker compose -f $DOCKER_COMPOSE_FILE up -d user_service"
echo "root:$PASSWORD" | docker --context $USERNAME exec $USERNAME -i root chpasswd
docker --context $USERNAME exec $USERNAME usermod -aG www-data root > /dev/null 2>&1
docker --context $USERNAME exec $USERNAME usermod -aG root www-data > /dev/null 2>&1
docker --context $USERNAME exec $USERNAME chmod -R g+w /var/www/html/ > /dev/null 2>&1
docker --context $USERNAME exec $USERNAME service ssh start > /dev/null 2>&1
exit 0;