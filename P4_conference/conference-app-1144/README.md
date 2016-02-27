# Leafer's Conference on App Engine

Leafer's Conference deployed on App Engine is a project created by [Marie Leaf](https://twitter.com/mleafer), for Project 4 of Udacity's Fullstack Nanodegree. Please see the [tasks](#Tasks) to see the full functionality that was built on top of the existing starter code. All functions are testable via Google's APIs Explorer.


### Table of contents

* [Quick Start](#quick-start)
* [Creator](#creator)
* [Concepts](#concepts)
* [Tasks](#Tasks)


## Products
[App Engine](https://developers.google.com/appengine)


## APIs
- [Google Cloud Endpoints](https://developers.google.com/appengine/docs/python/endpoints/)

## Quick Start
1. Update the value of `application` in `app.yaml` to the app ID you
   have registered in the App Engine admin console and would like to use to host
   your instance of this sample.
1. Update the values at the top of `settings.py` to
   reflect the respective client IDs you have registered in the
   [Developer Console](https://console.developers.google.com/)
1. Update the value of CLIENT_ID in `static/js/app.js` to the Web client ID
1. (Optional) Mark the configuration files as unchanged as follows:
   `$ git update-index --assume-unchanged app.yaml settings.py static/js/app.js`
1. Run the app with the devserver using `dev_appserver.py DIR`, and ensure it's running by visiting your local server's address (by default [localhost:8080](https://localhost:8080/).)
1. (Optional) Generate your client library(ies) with [the endpoints tool](https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool).
1. Deploy your application.


### Creator

**Marie Leaf**

* <https://twitter.com/mleafer>
* <https://github.com/mleafer>

### Concepts
* Google Cloud Endpoints
* Google Developer Console
* ProtoRPC
* Advanced Datastore concepts (indexes, query restrictions, dynamic filters, transactions)
* Advanced App Engine topics (NDB, memcache, task queues, cron jobs, push/pull queues, edge caching, modules)

### Tasks

__Task 1: Session and Speaker Class Design Choices__

__Task 2: Add Sessions to User Wishlist__

__Task 3: Work on indexes and queries__

__Task 4: Add a Task__


### Resources

[Cloud Endpoints Tutorial](http://rominirani.com/2014/01/10/google-cloud-endpoints-tutorial-part-1/)

https://cloud.google.com/appengine/docs/python/endpoints/create_api

https://www.youtube.com/watch?v=uy0tP6_kWJ4