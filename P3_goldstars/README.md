# Leafer's Gold Stars

Leafer's Gold Stars is equal parts motivational and competitive scoreboard between friends to award and earn stars. Users are able to store a list of event items within a variety of categories to keep track of stars earned. It provides a user registration and authentication system with defense against cross-site request forgery. Registered users (anyone with a Facebook or Google account) have the ability to post, edit and delete their own items. Created by [Marie Leaf](https://twitter.com/mleafer), for Project 3 of Udacity's Fullstack Nanodegree. It uses SeaSurf Flask extension to prevent cross-site request forgery.

<!--How to run-->
<!--This simple web application uses GitHub for authorization and authentication. To simulate security best practices, the API keys are not in the main application file or hard-coded. However, to facilitate grading, a shell script, export_keys.sh, is available to export API keys (current as of the time of submission) to server environment variables.-->


### Table of contents

* [Quick start](#quick-start)
* [Creator](#creator)
* [Concepts](#concepts)

### Quick start

* [Download the latest release](https://github.com/mleafer/fullstacknanodegree/archive/master.zip) .
* Set up your [Vagrant Machine](https://www.vagrantup.com/), and [Virtual Box](https://www.virtualbox.org/).
* Virtual Box
* Clone the [Fullstack VM Repo](https://github.com/udacity/fullstack-nanodegree-vm) for config files. 
* Initialize the VM via `vagrant up`
* Connect to the VM via `vagrant ssh`
* (Optional) Obtain your own Google/Facebook oAuth API keys be registering new applications.
* (Optional) Inside the VM, export your own API keys to files: 'client_secrets.json' and 'fb_client_secrets.json'.
* Navigate to catalog directory `cd /vagrant/P3_goldstars`
* Run `python goldstars.py` to launch the server
* Go to [localhost:5000](http://localhost:5000/domains/) to use the app locally! 


### Creator

**Marie Leaf**

* <https://twitter.com/mleafer>
* <https://github.com/mleafer>

### Concepts 
* Iterative Development
* Mock-ups
* Frameworks + Databases
* Routing + url_for
* Templates + Forms
* CRUD Functionality
* API Endpoints + JSON Messages
* Styling with CSS + * Message Flashing
* Local Permission Systems