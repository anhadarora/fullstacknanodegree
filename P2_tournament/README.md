# Leafer's Tournament

Leafer's Tournament runs a Swiss-Style tournament and supports more than one tournament in the database. Created by [Marie Leaf](https://twitter.com/mleafer), for Project 2 of Udacity's Fullstack Nanodegree.


### Table of contents

* [Quick start](#quick-start)
* [Creator](#creator)
* [Concepts](#concepts)

### Quick start

* [Download the latest release](https://github.com/mleafer/fullstacknanodegree.git).
* Set up your Vagrant Machine, and Virtual Box
* Install [Python 2.7.9](https://www.python.org/downloads/).
* Install [PostgreSQL](http://www.postgresql.org/download/).
⋅⋅* Ensure PostgreSQL is set up
⋅⋅⋅```vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ psql
⋅⋅⋅psql (9.3.5)
⋅⋅⋅Type "help" for help.```
* Create database
⋅```vagrant=> CREATE DATABASE tournament;
⋅CREATE DATABASE
⋅vagrant=> \q```
*Load SQL schema into database
⋅```vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ psql tournament < tournament.sql```
* Open and run tournament_test.py in your terminal
⋅```vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ python tournament_test.py```
⋅All tests should pass!
* (This was run on Linux, Mac OS X)

### Creator

**Marie Leaf**

* <https://twitter.com/mleafer>
* <https://github.com/mleafer>


### Concepts
* PostgreSQL
* Database schema design
* Proper relationship architecture
