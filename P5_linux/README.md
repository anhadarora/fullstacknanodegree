# Leafer's Linux

Leafer's Linux takes a baseline installation of a Linux distribution on a virtual machine and prepares it to host web applications, to include installing updates, secures it from a number of attack vectors and installs/configures web and database servers. Created by [Marie Leaf](https://twitter.com/mleafer), for Project 5 of Udacity's Fullstack Nanodegree.


### Table of contents

[Access](#access)
[Installation Summary](#installation-summary)
[Creator](#creator)
[Concepts](#concepts)
[Resources](#resources)

### Access

* [Download the latest release](https://github.com/mleafer/fullstacknanodegree/archive/master.zip).

__Server Details__

Server IP address: 52-34-14-120

SSH port: 2200

Application URL: http://ec2-52-34-14-120.us-west-2.compute.amazonaws.com/ 

If private key installed: Connect ssh grader@52.34.14.120 -p 2200 -i ~/.ssh/id_rsa

### Installation Summary
A summary of software installed and configuration changes made. Refer to the .bash_history files on the server!
ssh -i ~/.ssh/udacity_key.rsa root@52.34.215.3

__Software Installed__

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

__Configuration__

Update all currently installed packages
`sudo apt-get update`
`sudo apt-get upgrade -y`

Configure Automatic Security Updates
`sudo apt-get install unattended-upgrades`
`sudo dpkg-reconfigure -plow unattended-upgrades`

Create a new user named grader
`sudo adduser grader`

Give the user grader permission to sudo
`echo "grader ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/grader`

Set up SSH Authentication
Generate SSH key pairs, then copy the contents of the generated .pub file to the clipboard

Run on Local Machine
`ssh-keygen -t rsa -b 2048 -C "Just some comment"`
Configure public key on server. As the grader user paste .pub file contents in to .ssh/authorized_key file

Run on server
`su grader`
`mkdir ~/.ssh`
`touch ~/.ssh/authorized_keys`

Set correct permissions
`chmod 700 ~/.ssh`
`chmod 644 ~/.ssh/authorized_keys`

**Change the SSH port from 22 to 2200**

Open SSH config file
`nano /etc/ssh/sshd_config`

Change Port 22 to Port 2200

Remote login of the root user has been disabled

Open SSH config file

`nano /etc/ssh/sshd_config`

Ensure PermitRootLogin has a value `no`

Enforce SSH Authentication (i.e prevent password login)

Open SSH config file

`sudo nano /etc/ssh/sshd_config`
Ensure PasswordAuthentication has a value `no`

Restart SSH service
`sudo service ssh restart`

Configure the Uncomplicated Firewall (UFW)

Block all incoming requests: `sudo ufw default deny incoming`  
Allow all outgoing requests: `sudo ufw default allow outgoing`  
Allow incoming connections for SSH (port 2200): `sudo ufw allow 2200/tcp`  
Allow incoming connections for HTTP (port 80): `sudo ufw allow www`  
Allow incoming connections for NTP (port 123): `sudo ufw allow ntp`  
Enable ufw: `sudo ufw enable`  and answer `y` at the prompt
Reboot: `sudo reboot`

Configure the local timezone to UTC

Reconfiguring the tzdata package: `sudo dpkg-reconfigure tzdata`

# select `None of the above` then `UTC`

Install and configure Apache to serve a Python mod_wsgi application

Install required packages

`sudo apt-get install apache2`
`sudo apt-get install libapache2-mod-wsgi`

Install and configure PostgreSQL: `sudo apt-get install postgresql`

Create a new user named catalog that has limited permissions to your catalog application database

Change to postgres user

`sudo -i -u postgres`

Create new dastbase user catalog

```postgres@server:~$ createuser --interactive -P
Enter name of role to add: catalog
Enter password for new role:
Enter it again:
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) n
Shall the new role be allowed to create more new roles? (y/n) n
```

Create catalog Database

```postgres:~$ psql
CREATE DATABASE catalog;
\q
```
logout of postgres user

`exit`

Install git, clone and setup Catalog App project

`Install git`

sudo apt-get install git
clone repo

Protect .git directory

`sudo chmod 700 /var/www/catalog/catalog/.git`

Install application dependences
```
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
```
Create a wsgi file entry point to work with mod_wsgi
```
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/P3_goldstars/")

from P3_goldstars import app as application
application.secret_key = 'super_secret_key'```

Configure and Enable New Virtual Host


`sudo nano /etc/apache2/sites-available/P3_goldstars.conf`


Update last line of `/etc/apache2/sites-enabled/P3_goldstars.conf` to handle requests using the WSGI module, add the following line right before the closing line:

`WSGIScriptAlias / /var/www/P3_goldstars/P3_goldstars/myapp.wsgi`

Update Database connection string in database_setup to the following:

postgresql://catalog:password@localhost/catalog
__Ensure oauth tokens are correct

Restart Apache

sudo service apache2 restart

__Reconfigure oauth permissions__

change my clients_secrets.json file and "authorized redirect URIs" in Google developers console

`"redirect_uris":["http://ec2-52-34-14-120.us.west-2.compute.amazonaws.com/oauth2callback"]`
### Creator

**Marie Leaf**

* <https://twitter.com/mleafer>
* <https://github.com/mleafer>

### Concepts



### Resources
A list of any third-party resources you made use of to complete this project.
http://askubuntu.com/questions/15433/unable-to-lock-the-administration-directory-var-lib-dpkg-is-another-process
5

[VIM editor cheatsheet](http://www.fprintf.net/vimCheatSheet.html)
https://help.ubuntu.com/community/Sudoers

[Digital Ocean Tutorial Deploying Flask on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/#configuring-apache
