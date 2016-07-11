#!/bin/sh

sudo add-apt-repository ppa:nginx/stable
sudo apt-get update
sudo apt-get install python-virtualenv python-pip python-dev nginx libmemcached-dev memcached git -y
# libs for pillow
sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk -y
# ubuntu 12.04 see https://github.com/python-pillow/Pillow/blob/master/docs/installation.rst
# sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk -y

sudo mkdir /opt/anaf
sudo chown $USER /opt/anaf
cd /opt/anaf

virtualenv env
source env/bin/activate
pip install -U setuptools pip
pip install uwsgi pylibmc

pip install https://github.com/tovmeod/anaf/archive/master.zip

# see http://www.postgresql.org/download/linux/ubuntu/
# this should work at least for lucid (10.04), precise (12.04), trusty (14.04) and utopic (14.10)
echo "deb http://apt.postgresql.org/pub/repos/apt/ "$(lsb_release -a | grep Codename | awk -F' ' '{print $2}')"-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install postgresql-9.5 libpq-dev -y
sudo -u postgres createuser --pwprompt anaf
# sudo -u postgres psql -c "ALTER USER anaf WITH ENCRYPTED PASSWORD 'anaf_db_password';"
sudo -u postgres createdb anaf --owner=anaf
pip install psycopg2
cd anaf
python manage.py collectstatic --noinput
python manage.py installdb

# load initial data  TODO create an initial data migration

#add uwsgi to upstart
sudo ln -s /opt/anaf/upstart.conf  /etc/init/anaf.conf
sudo initctl reload-configuration
sudo start anaf
sudo ln -s /opt/anaf/nginx.conf  /etc/nginx/sites-enabled/anaf
sudo rm  /etc/nginx/sites-enabled/default
sudo nginx -s reload

# optional: get ssl certificates
# to generate your dhparam.pem file, run in the terminal
# openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
# git clone https://github.com/letsencrypt/letsencrypt
# cd letsencrypt/
# ~/.local/share/letsencrypt/bin/pip install -U letsencrypt-nginx
# ./letsencrypt-auto --nginx