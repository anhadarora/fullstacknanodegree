# Leafer's Tournament

Leafer's Tournament runs a Swiss-Style tournament and supports more than one tournament in the database. Created by [Marie Leaf](https://twitter.com/mleafer), for Project 2 of Udacity's Fullstack Nanodegree.


### Table of contents

* [Quick start](#quick-start)
* [Creator](#creator)
* [Concepts](#concepts)

### Quick start

* [Download the latest release](https://github.com/mleafer/fullstacknanodegree.git).
* Set up your [Vagrant Machine](https://www.vagrantup.com/), and [Virtual Box](https://www.virtualbox.org/).
* Clone the [Fullstack VM Repo](https://github.com/udacity/fullstack-nanodegree-vm) for config files. 
* Install [Python 2.7.9](https://www.python.org/downloads/).
* Install [PostgreSQL](http://www.postgresql.org/download/).
  To ensure PostgreSQL is set up:
   ```vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ psql
   ```
  Terminal should return:
   ```psql (9.3.5)
   ```
* Create database

 ```vagrant=> CREATE DATABASE tournament;
 CREATE DATABASE
 vagrant=> \q
 ```

* Load SQL schema into database: 
 ```vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ psql tournament < tournament.sql
 ```

* Open and run tournament_test.py in your terminal, all tests should pass!
 ```vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ python tournament_test.py
 ```

* (This was run on Linux, Mac OS X)

### Creator

**Marie Leaf**

* <https://twitter.com/mleafer>
* <https://github.com/mleafer>


### Concepts
* PostgreSQL
* Database schema design
* Proper relationship architecture