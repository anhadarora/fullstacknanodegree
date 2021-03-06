# Leafer's Conference on App Engine

Leafer's Conference deployed on App Engine is a project created by [Marie Leaf](https://twitter.com/mleafer), for Project 4 of Udacity's Fullstack Nanodegree. Please see the [tasks](#Tasks) to see the full functionality that was built on top of the existing starter code. All functions are testable via Google's APIs Explorer.


### Table of contents

* [Quick Start](#quick-start)
* [Creator](#creator)
* [Concepts](#concepts)
* [Tasks](#Tasks)
* [Resources](#Resources)
* [Xtra Tips](#Xtra Tips)


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
* Google Cloud Endpoints(write/call endpoint functions using JS client library, use APIs explorer for publicly available google apis)
* Google Developer Console
* ProtoRPC
* Advanced Datastore concepts (indexes, query restrictions, dynamic filters, transactions)
* Advanced App Engine topics (NDB, memcache, task queues, cron jobs, push/pull queues, edge caching, modules)


### Tasks

__Task 1: Session and Speaker Class Design Choices__

I created sessions as a separate 'kind' object to store different entities with speaker as a property. The speaker was not created as separate object, but kept as a property to mitigate administrative issues and to ensure centrality of all 'people' objects. (e.g. if you need comprehensive user/headcount list for administrative purposes)

Sessions were created with a parent conference key, and created to ensure that the user creating the session is the organizer of the parent conference. 

__Task 2: Add Sessions to User Wishlist__  
Users can add, retrieve, and delete sessions from their wishlist.

__Task 3: Work on indexes and queries__

3.1 - Make sure the indexes support the type of queries required by the new Endpoints methods.  
*Please see index.yaml file.*

3.2 - Come up with two additional queries  

*3.2.1 - Query sessions held today: useful for seeing a daily agenda for a user.*  
`getSessionsToday`  
*3.2.2 - Query past sessions: useful to see past sessions, and to be used in follow-on function to delete past sessions*  
`getPastSessions`  

3.3 - Solve the following 'non-workshop', 'before 7 pm' query problem  
*This query requires an inequality filter on two properties, and datastore only supports inequality filtering on a single property (not multiple properties)*

*One possible solution is to break this into two datastore queries, first filtering the session by type, populating an array of keys, and then querying this array of keys to match time before 7 pm.*

*Another possible solution (the solution I implemented) would be to query sessions before 7, and then remove the sessions where 'typeOfSession == 'workshop''. I chose this implementation due to less processing steps than the first solution proposed (which would be inefficient with large datasets.)*  
`getSessionsByTypeTime`  

__Task 4: Add a Task__  
When a new session is added to a conference, the speaker is checked. If there is more than one session by this speaker at this conference, a new Memcache entry is added that features the speaker and session names. The logic is handled using App Engine's Task Queue.

### Resources

[Cloud Endpoints Tutorial](http://rominirani.com/2014/01/10/google-cloud-endpoints-tutorial-part-1/)

https://cloud.google.com/appengine/docs/python/endpoints/create_api

https://www.youtube.com/watch?v=uy0tP6_kWJ4

### Xtra Tips

To test API locally (so you dont have to debug through google server):
in terminal: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080`
go to `http://localhost:8000/` - click on “default” to see web UI
go to `localhost:8080/_ah/api/explorer` - to see api explorer