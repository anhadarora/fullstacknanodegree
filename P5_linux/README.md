# Leafer's Linux

Leafer's Linux {insert functions} Created by [Marie Leaf](https://twitter.com/mleafer), for Project 5 of Udacity's Fullstack Nanodegree. 


### Table of contents

* [Quick start](#quick-start)
* [Creator](#creator)
* [Concepts](#concepts)

### Quick start

* [Download the latest release](https://github.com/mleafer/fullstacknanodegree/archive/master.zip).
* Ensure you have [Vagrant Machine](https://www.vagrantup.com/), and [Virtual Box](https://www.virtualbox.org/) installed.
* Initialize the VM via `vagrant up`
* Connect to the VM via `vagrant ssh`
* (Optional) Obtain your own [Google](https://console.developers.google.com)/[Facebook](https://developers.facebook.com/) oAuth API keys.
* (Optional) Inside the VM, export your own API keys to files: 'client_secrets.json' and 'fb_client_secrets.json'.
* Navigate to catalog directory `cd /vagrant/P3_goldstars`
* Run `python goldstars.py` to launch the server
* Go to [localhost:5000](http://localhost:5000/domains/) to use the app locally! 


### Creator

**Marie Leaf**

* <https://twitter.com/mleafer>
* <https://github.com/mleafer>

### Concepts 


Take a baseline installation of a Linux distribution on a virtual machine and prepare it to host a web applications, to include installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

Server Details

Server IP address: 52.27.62.61

SSH port: 2200

Application URL: http://52.27.62.61

Software Installed

Apache2
PostgreSQL
bleach
flask-seasurf
git
github-flask
httplib2
libapache2-mod-wsgi
oauth2client
python-flask
python-pip
python-psycopg2
python-sqlalchemy
requests
Configuration

Update all currently installed packages

sudo apt-get update
sudo apt-get upgrade -y
Configure Automatic Security Updates

sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
Create a new user named grader

adduser grader
Give the user grader permission to sudo

echo "grader ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/grader
Set up SSH Authentication

Generate SSH key pairs, then copy the contents of the generated .pub file to the clipboard

# RUN ON LOCAL MACHINE
ssh-keygen -t rsa -b 2048 -C "Just some comment"
Configure public key on server. As the grader user paste .pub file contents in to .ssh/authorized_key file

# RUN ON SERVER
su grader
mkdir ~/.ssh
vim ~/.ssh/authorized_keys
Set correct permissions

chmod 700 ~/.ssh
chmod 644 ~/.ssh/authorized_keys
Change the SSH port from 22 to 2200

Open SSH config file

vim /etc/ssh/sshd_config
Change Port 22 to Port 2200

Remote login of the root user has been disabled

Open SSH config file

vim /etc/ssh/sshd_config
Ensure PermitRootLogin has a value no`

Enforce SSH Authentication (i.e prevent password login)

Open SSH config file

vim /etc/ssh/sshd_config
Ensure PasswordAuthentication has a value no`

Restart SSH service

sudo service ssh restart
Configure the Uncomplicated Firewall (UFW)

Block all incoming requests

sudo ufw default deny incoming
Allow all outgoing requests

sudo ufw default allow outgoing
Allowing incoming connections for SSH (port 2200)

sudo ufw allow 2200/tcp
Allowing incoming connections for HTTP (port 80)

sudo ufw allow www
Allowing incoming connections for NTP (port 123)

sudo ufw allow ntp
Enable ufw

sudo ufw enable
Configure the local timezone to UTC

Reconfiguring the tzdata package

sudo dpkg-reconfigure tzdata
# select `None of the above` then `UTC`
Install and configure Apache to serve a Python mod_wsgi application

Install required packages

sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
Install and configure PostgreSQL

sudo apt-get install postgresql
Create a new user named catalog that has limited permissions to your catalog application database

Change to postgres user

sudo -i -u postgres
Create new dastbase user catalog

postgres@server:~$ createuser --interactive -P
Enter name of role to add: catalog
Enter password for new role:
Enter it again:
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) n
Shall the new role be allowed to create more new roles? (y/n) n
Create catalog Database

postgres:~$ psql
CREATE DATABASE catalog;
\q
logout of postgres user

exit
Install git, clone and setup Catalog App project

Install git

sudo apt-get install git
clone repo

Protect .git directory

sudo chmod 700 /var/www/catalog/catalog/.git
Install application dependences

sudo apt-get -qqy install python-psycopg2
sudo apt-get -qqy install python-flask
sudo apt-get -qqy install python-sqlalchemy
sudo apt-get -qqy install python-pip
sudo pip install bleach
sudo pip install flask-seasurf
sudo pip install github-flask
sudo pip install httplib2
sudo pip install oauth2client
sudo pip install requests
Create a wsgi file entry point to work with mod_wsgi

#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalog/catalog")

from catalog import app as application
Update last line of /etc/apache2/sites-enabled/000-default.conf to handle requests using the WSGI module, add the following line right before the closing line:

WSGIScriptAlias / /var/www/catalog/catalog/myapp.wsgi
Update Database connection string in database_setup to the following:

postgresql://catalog:password@localhost/catalog
Ensure oauth tokens are correct

Restart Apache

sudo service apache2 restart