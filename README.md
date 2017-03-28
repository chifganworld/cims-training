
# Composants RapidPro

## PostgreSQL

* Base de données
 * Orgs, Flows, Runs, Msgs, Users, etc.
* BDD géographique

## redis

* BDD clé-valeur
* Stockage temporaire
* Données mises en cache (temba)
* Données des queues redis
* Données des queues mage

## temba

* Application Web de RapidPro
* Python+Django et 60 autres bibliothèques
* uWSGI: interface WSGI/python pour nginx

## Web Stack
* LESS (compilateur CSS)
* Coffeescript (compilateur JavaScript)
* NodeJS + bower (gestion de paquets JavaScript: 40 dépendances)

## Celery

* Gère toutes les tâches asynchrones
* broker (default, handler, msgs, flows)
* taches périodiques et planifiées

## mage

* Serveur Web
* Java
* Gère le callback de Twitter (lecture-seule)

## nginx

* Serveur Web (server_name)
* Sert les fichiers *statiques*:
 * CSS, JS (rapidpro et dépendances)
 * dossier `/media` (imports, exports, logos)
* Certificat SSL et redirection 


# Environment de test

Réplique réaliste d'un serveur existant. Basé sur un Debian récent:

* Version des paquets (postgres, nginx, redis, java)
* systemd (upstart, sysvinit)

## Preparation

* VirtualBox
	Preferences > Network > Host-only networks
		Add vboxnetX 
			DHCP
			192.168.60.1 255.255.255.0
			192.168.60.2 192.168.60.50

* debian64 VM
	* 2GB RAM
	* 20GB dynamic HDD
	* Network
		1. NAT
		2. host-only @ vboxnetX
	* Optical drive: debian-8.7.1-amd64-netinst.iso
	* Install
		* English > Africa > Tunisia > en_US.UTF-8 > American English (keymap)
	   * hostname: rapidpro
	   * domain: cims
	   * root password: tunis
	   * Superman / super / super
	   * Guided, entire disk, single partition
	   * Mirror: Tunisia (debian.mirror.tn)
	   * Packages: ssh, std system utilities
	   * Install grub (/dev/sda)
	* Initial config (root)
	   * `/etc/network/interfaces`
```
allow-hotplug eth1
iface eth1 inet dhcp
```
      * `reboot -h now`
      * Install ssh-keys (super and root)
      * Install sudo: `apt install sudo && usermod -a -G sudo super`
      * Install Vim `apt install ntp screen vim && wget -O ~/.vimrc https://raw.githubusercontent.com/rgaudin/MiniVim/master/vimrc && cp ~/.vimrc /home/super/.vimrc && chown super:super /home/super/.vimrc`

## Utilisation

### Installation

* Install VirtualBox
* Install Putty (Windows)
* Add key to putty
* Import VM

### Première connexion

* Reconfigurer clavier

```
sudo dpkg-reconfigure keyboard-configuration
sudo service keyboard-setup restart
```

```
/etc/profile.d/proxy.sh

export http_proxy="formation18:form15*+@172.20.0.2:3113"
```

# Installation

Concepts: URL, socket, ports, daemon

## PostgreSQL

* https://www.postgresql.org/docs/9.4/static
* `apt install postgresql-9.4 postgresql-9.4-postgis-2.1`

* `vim /etc/postgresql/9.4/main/postgresql.conf`: configuration générale
 * paramètrages (chemins, options)
 * optimisations (algorithmes, tailles des buffers)
 * **listen_addresses = 'localhost'**
 * **port = 5432**
* `pg_hba.conf`: configuration des accès à postgres.

* Création compte et base dédiés à RapidPro

```
sudo su - postgres
psql -c "CREATE USER rapidpro WITH PASSWORD 'rapidpro';"
psql -c "CREATE DATABASE rapidpro;"
psql -c "GRANT CREATE,CONNECT,TEMP ON DATABASE rapidpro to rapidpro;"
```

* create extension pour postgis

```
psql -d rapidpro -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION hstore;"
```

* DSN: `postgresql://rapidpro:rapidpro@localhost/rapidpro`
* Tests 

`psql postgresql://rapidpro:rapidpro@localhost/rapidpro`

```
\d
\dt
CREATE TABLE test();
\dt
DROP TABLE test;
\dt
```

* Backup

```
sudo su - postgres -c "pg_dump rapidpro > /tmp/postgres-rapidpro.sql"
sudo su - postgres -c "pg_dumpall > /tmp/postgress-all.sql"
```

* Restore

```
sudo su - postgres -c "psql --set ON_ERROR_STOP=on rapidpro < /tmp/postgres-rapidpro.sql"
sudo su - postgres -c "psql --set ON_ERROR_STOP=on -f /tmp/postgres-rapidpro.sql postgres"
```

* Vérifier démarrage: `systemctl status postgresql`
* [psql cheatsheet](https://gist.github.com/Kartones/dd3ff5ec5ea238d4c546)

## redis

`apt install redis-server redis-tools`

* `/etc/redis/redis.conf`
 * **port 6379**
 * **bind 127.0.0.1**
 * **databases 16**

* test `redis-cli`

```
SET "name" "Tunis"
GET "name"
DEL "name"
GET "name"
LPUSH "names" "Tunis"
LPUSH "names" "Carthage"
LLEN "names"
LPOP "names"
LLEN "names"
```
* Vérifier démarrage: `systemctl status redis-server`


## update
* Changer `mirror.debian.tn` par `ftp.fr.debian.org` dans /etc/apt/sources.list`
* `apt update && apt upgrade`


## SSL certificate

```
openssl dhparam -dsaparam -out /etc/ssl/certs/dhparam.pem 4096
openssl req -x509 -nodes -days 1095 -newkey rsa:2048 -keyout /etc/ssl/private/rapidpro-self.key -out /etc/ssl/certs/rapidpro-self.crt
```

* Verify informations

```
openssl x509 -in /etc/ssl/certs/rapidpro-self.crt -text -noout

openssl x509 -noout -modulus -in /etc/ssl/certs/rapidpro-self.crt| openssl md5
openssl rsa -noout -modulus -in /etc/ssl/private/rapidpro-self.key| openssl md5
```

## nginx (part1)

* `apt install nginx`
* `mkdir -p /var/log/rapidpro/`
* Copier `/etc/nginx/sites-available/rapidpro`
* `ln -s /etc/nginx/sites-available/rapidpro /etc/nginx/sites-enabled/rapidpro`

```
server {
    listen 80;
    listen [::]:80;

    server_name 192.168.60.2 localhost rapidpro aigri.ml www.agri.ml;

    access_log    /var/log/rapidpro/rapidpro-access.log combined;
    error_log     /var/log/rapidpro/rapidpro-error.log;

    # entity size
    client_max_body_size 50m;

    # static files
    location /sitestatic  {
        alias /home/rapidpro/temba/sitestatic;
    }

    location / {
        proxy_pass        http://localhost:8001;
        proxy_read_timeout 300s;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    }
}

server {
    listen 443;
    listen [::]:443;

    ssl_certificate      /etc/ssl/certs/rapidpro-self.crt;
    ssl_certificate_key  /etc/ssl/private/rapidpro-self.key;

    # tell client/browser to always use https
    add_header Strict-Transport-Security max-age=31536000;

    location / {
        proxy_pass        http://localhost:8001;
        proxy_read_timeout 300s;

        proxy_redirect     off;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
    }
}
```
* Vérifier démarrage: `systemctl status nginx`
* redémarrage: `nginx -s reload`
* Tester `http://192.168.60.2` et `https://192.168.60.2`

## temba

* Dependencies
* `apt install git zlib1g liblzma-dev`
* `apt install libncurses5 libncurses-dev libreadline-dev libreadline5`
* `apt install libxslt1.1 xsltproc libxml2-dev libxslt1-dev`
* `apt install libgpg-error-dev libffi6 libffi-dev`
* `apt install perl libpcre3 tcl shadowsocks`
* `apt install libgd3 libjpeg62 libjpeg-dev libpng12-0 libpng-dev`
* `apt install python2.7-dev python-virtualenv python-pip python-lxml libpq-dev python-psycopg2 python-celery`
* `apt install npm nodejs`
* `npm install -g less coffee-script bower`
* `ln -s /usr/bin/nodejs /usr/bin/node`
* create user `useradd -g www-data -m -N -s /bin/bash rapidpro`
* `cp -r /home/super/.ssh /home/rapidpro/`
* `chown -R rapidpro:www-data /home/rapidpro/.ssh/`

**En tant que `rapidpro`** (`su - rapidpro`)

* `mkdir .virtualenvs && virtualenv .virtualenvs/rapidpro`
* `mkdir -p src`

```
git clone https://github.com/rapidpro/rapidpro.git src/temba-`date +"%s"` --depth 1
```
* `ln -s src/temba* temba`
* `vim ~/.bashrc`:

```
source ~/.virtualenvs/rapidpro/bin/activate
cd ~/temba"
```
* exit

## Fichiers de configuration

`git clone https://github.com/rgaudin/cims-training.git ~/src/training`

## temba (en tant que `rapidpro`)

* `pip install -r pip-freeze.txt --allow-all-external`
* `pip install -U pip`
* `pip install -U setuptools`
* `pip install uwsgi`
* copy `temba/settings.py`
* `./manage.py migrate --noinput`
* `./manage.py collectstatic --noinput`
* `mkdir -p ~/{sitestatic,media}`
* `chmod 755 ~/{sitestatic,media}`
* copy `uwsgi.ini`
* test `./manage.py runserver 0.0.0.0:8000` via `http://192.168.60.2:8000`
* copy `/etc/systemd/system/rapidpro.service`
* `systemctl status rapidpro`
* `systemctl daemon-reload`
* `systemctl enable rapidpro`
* `systemctl start rapidpro`

## nginx (part2)

```
#root /home/super;
#autoindex on;
proxy_pass        http://localhost:8001;
```

## GIS data

**Tunisia OSM relation ID**: R192757

```
mkdir -p ~/posm-extracts
cd ~/posm-extracts
wget https://github.com/nyaruka/posm-extracts/raw/master/geojson/R192757admin0_simplified.json
wget https://github.com/nyaruka/posm-extracts/raw/master/geojson/R192757admin1_simplified.json
wget https://github.com/nyaruka/posm-extracts/raw/master/geojson/R192757admin2_simplified.json
cd ~/temba
./manage.py import_geojson ~/posm-extracts/*_simplified.json
```

## WebUI Configuration

* Log onto https://rapidpro (root / admin)
* https://rapidpro/org/grant/
* https://rapidpro/org/home/
* Location -> Tunisie

## Celery

```
mkdir -p /var/log/celery/
chgrp www-data /var/log/celery/
chmod 775 /var/log/celery/
```
* copy `/etc/systemd/system/celerybeat.service`
* `systemctl status celerybeat`
* `systemctl enable celerybeat`
* `systemctl start celerybeat`
* copy `/etc/systemd/system/celery.service`
* `systemctl status celery`
* `systemctl daemon-reload`
* `systemctl enable celery`
* `systemctl start celery`

## mage

```
apt install software-properties-common
add-apt-repository "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main"
apt intall oracle-java8-installer
update-alternatives --config java
```
* get token from webUI (https://rapidpro/org/home/)
* copy `src/mage-0.1.82.jar`
* `mkdir -p ~/mage`
* `ln -s ~/src/mage-*.jar mage.jar`
* copy `config.yml` et `env.sh`
* `./env.sh java -jar mage.jar server config.yml`
* copy `/etc/systemd/system/mage.service`
* `systemctl status mage`
* `systemctl daemon-reload`
* `systemctl enable mage`
* `systemctl start mage`

## Update RapidPro

* git
* pip install
* migrate
* collectstatic
* restart
