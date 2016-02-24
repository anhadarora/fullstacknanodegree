# Leafer's Linux

Leafer's Linux takes a baseline installation of a Linux distribution on a virtual machine and prepares it to host web applications, to include installing updates, secures it from a number of attack vectors and installs/configures web and database servers. Created by [Marie Leaf](https://twitter.com/mleafer), for Project 5 of Udacity's Fullstack Nanodegree.


## Table of contents

[Access](#access)

[Installation Summary](#installation-summary)

[Creator](#creator)

[Concepts](#concepts)

[Resources](#resources)


## Access

* [Download the latest release](https://github.com/mleafer/fullstacknanodegree/archive/master.zip).

__Server Details__

Server IP address: 52-34-14-120

SSH port: 2200

Application URL: http://ec2-52-34-14-120.us-west-2.compute.amazonaws.com/ 

With private key installed: Connect ssh grader@52.34.14.120 -p 2200 -i ~/.ssh/id_rsa

## Installation Summary
A summary of software installed and configuration changes made. Refer to the .bash_history files on the server.
ssh -i ~/.ssh/udacity_key.rsa root@52.34.215.3

###Software Installed

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

###Configuration

__Update all currently installed packages__

`sudo apt-get update`

`sudo apt-get upgrade -y`


__Configure Automatic Security Updates__

`sudo apt-get install unattended-upgrades`

`sudo dpkg-reconfigure -plow unattended-upgrades`


__Create a new user named grader__

`sudo adduser grader`


__Give the user grader permission to sudo__

`echo "grader ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/grader`


__Set up SSH Authentication__

Generate SSH key pairs, then copy the contents of the generated .pub file to the clipboard


__Run on Local Machine__

`ssh-keygen -t rsa -b 2048 -C "Just some comment"`

Configure public key on server. As the grader user paste .pub file contents in to .ssh/authorized_key file


__Run on server__

`su grader`

`mkdir ~/.ssh`

`touch ~/.ssh/authorized_keys`


__Set correct permissions__

`chmod 700 ~/.ssh`

`chmod 644 ~/.ssh/authorized_keys`


__Change the SSH port from 22 to 2200__

Open SSH config file and change `Port 22` to `Port 2200`

`nano /etc/ssh/sshd_config`

__Disable remote login of root user__

In SSH config file, ensure `PermitRootLogin` has a value `no`

__Enforce SSH Authentication (i.e prevent password login)__

In SSH config file, ensure `PasswordAuthentication` has a value `no`

Restart SSH service

`sudo service ssh restart`


__Configure the Uncomplicated Firewall (UFW)__

Block all incoming requests: `sudo ufw default deny incoming`  
Allow all outgoing requests: `sudo ufw default allow outgoing`  
Allow incoming connections for SSH (port 2200): `sudo ufw allow 2200/tcp`  
Allow incoming connections for HTTP (port 80): `sudo ufw allow www`  
Allow incoming connections for NTP (port 123): `sudo ufw allow ntp`  
Enable ufw: `sudo ufw enable`  and answer `y` at the prompt
Reboot: `sudo reboot`


__Configure the local timezone to UTC__

Reconfiguring the tzdata package: `sudo dpkg-reconfigure tzdata`

select `None of the above` then `UTC`

__Install required packages__

Install and configure Apache to serve a Python mod_wsgi application

```sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
```

Install and configure PostgreSQL: `sudo apt-get install postgresql`  
Check if no remote connections are allowed: `sudo vim /etc/postgresql/9.3/main/pg_hba.conf`  

__Create a new user named `catalog` __
With limited permissions to your catalog application database

Change to postgres user: `sudo -i -u postgres`

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

logout of postgres user: `exit`

Install git, clone and setup Catalog App project: `Install git`

``sudo apt-get install git``

Clone Goldstars repo and protect .git directory
`sudo git clone https://github.com/mleafer/fullstacknanodegree/tree/master/P3_goldstars`  
`sudo chmod 700 /var/www/P3_goldstars/.git`

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
application.secret_key = 'super_secret_key'
```

__Configure and Enable New Virtual Host__

`sudo nano /etc/apache2/sites-available/P3_goldstars.conf`

Update last line of `/etc/apache2/sites-enabled/P3_goldstars.conf` to handle requests using the WSGI module, add the following line right before the closing line:  
`WSGIScriptAlias / /var/www/P3_goldstars/P3_goldstars/myapp.wsgi`

Update Database connection string in database_setup.py, and \__init__.py to the following:
`postgresql://catalog:password@localhost/catalog`

Turn off debug mode in \__init.py__ before deploying app - Debug mode in a production environment is a [major security risk](http://flask.pocoo.org/docs/0.10/quickstart/#debug-mode)

Restart Apache

`sudo service apache2 restart`

__Reconfigure oauth permissions__

change path in \__init__.py to correctly read client_secrets.json
`CLIENT_ID = json.loads(open('/var/www/P3_goldstars/P3_goldstars/client_secrets.json','r').read())['web']['client_id']`

use os.chdir(dir)? 

to see apache log: `sudo tail /var/log/apache2/error.log`

change my clients_secrets.json file and "authorized redirect URIs" in Google developers console

`"redirect_uris":["http://ec2-52-34-14-120.us.west-2.compute.amazonaws.com/oauth2callback"]`

Change Facebook oAuth settings to list `http://ec2-52-34-14-120.us-west-2.compute.amazonaws.com/` as site URL

__Install Unattended Upgrades__

`apt-get install unattended-upgrades`
`sudo nano /etc/apt/apt.conf.d/50unattended-upgrades` 
un-comment the line `${distro_id}:${distro_codename}-updates` so updates are installed  
`sudo nano /etc/apt/apt.conf.d/02periodic` and add the following lines:  
```// Enable the update/upgrade script (0=disable) 
APT::Periodic::Enable "1"; 
// Do "apt-get update" automatically every n-days (0=disable) 
APT::Periodic::Update-Package-Lists "1"; 
// Do "apt-get upgrade --download-only" every n-days (0=disable) 
APT::Periodic::Download-Upgradeable-Packages "1"; 
// Run the "unattended-upgrade" security upgrade script 
// every n-days (0=disabled) 
// Requires the package "unattended-upgrades" and will write 
// a log in /var/log/unattended-upgrades 
APT::Periodic::Unattended-Upgrade "1"; 
// Do "apt-get autoclean" every n-days (0=disable) 
APT::Periodic::AutocleanInterval "7";
```

To check updates: `/var/log/apt/history.log`  

__Install monitoring application__  
that provides automated feedback on application availability status and system security alerts.


### Creator

**Marie Leaf**

* <https://twitter.com/mleafer>
* <https://github.com/mleafer>

### Concepts



### Resources
http://askubuntu.com/questions/15433/unable-to-lock-the-administration-directory-var-lib-dpkg-is-another-process
5

[VIM editor cheatsheet](http://www.fprintf.net/vimCheatSheet.html)
https://help.ubuntu.com/community/Sudoers

[Deploying Flask on Ubuntu - Tutorial](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/#configuring-apache

[Unattended Upgrades](https://www.howtoforge.com/how-to-configure-automatic-updates-on-debian-wheezy)

[Fail2Ban](http://www.fail2ban.org/wiki/index.php/MANUAL_0_8)  
[Fail2Ban Tutorial](https://www.digitalocean.com/community/tutorials/how-to-protect-ssh-with-fail2ban-on-ubuntu-14-04)  

[Munin](http://munin-monitoring.org/wiki/Documentation)  
[Munin Tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-munin-on-an-ubuntu-vps)