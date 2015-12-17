from flask import Flask, render_template, request, \
    redirect, url_for, flash, jsonify
# import module for authorization/authentication
from flask import session as login_session
import random, string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, domain, event, user
# create a flow object from the client's secret JSON file,
# which stores clientID, client secret, and oAuth parameters
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
# json module provides an API for converting in memory python objects
# to a serialized representation (json)
import json
# xml module... DELETE CLEAN
# from dict2xml import dict2xml
# converts the return value from a function into an object to send to client
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "healthitems-app"

app = Flask(__name__)

engine = create_engine('sqlite:///goldstarswithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

repo_uri = 'https://github.com/mleafer/fullstacknanodegree.git'
base_uri = '/domains/'
api_uri = base_uri + 'api/'

# Create a random anti-forgery state token with each GET request
@app.route('/login', methods=['GET', 'POST'])
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.
        digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Log-in to the site with a server side function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Confirm that token client sends to server = server sends to the client
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended use
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's client ID doesn't match app's."),
            401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    # stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user \
            is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info from Google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_ID = getUserID(login_session['email'])
    if not user_ID:
        user_ID = createUser(login_session)
    login_session['user_id'] = user_ID

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width:100px; height:100px; border-radius:150px; \
                -webkit-border-radius:150px; -moz-border-radius:150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Create a new user by extracting all the necessary data from the login_session
def createUser(login_session):
    newUser = user(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    newUser = session.query(user).filter_by(email=login_session['email']).one()
    return newUser.userID


def getUserInfo(userID):
    return session.query(user).filter_by(userID=userID).one()


def getUserID(email):
    try:
        getUser = session.query(user).filter_by(email=email).one()
        return getUser.userID
    except:
        return None


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token\
           &client_id=%s&client_secret=%s&fb_exchange_token=%s'\
            % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Store the token in the login_session for proper logout
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect\
           =0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius:\
     150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output


# DISCONNECT; revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Failed to revoke token for\
                                 given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s'\
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('domains'))
    else:
        flash("You were not logged in")
        return redirect(url_for('domains'))


# JSON APIs to view domain and event Information
@app.route('/domains.json')
def domainsJSON():
    domains = session.query(domain).all()
    return jsonify(domains=[c.serialize for c in domains])


@app.route('/domains/<int:domID>/events.json')
def domeventsJSON(domID):
    dom = session.query(domain).filter_by(domID=domID).one()
    events = session.query(event).filter_by(domID=domID).all()
    return jsonify(events=[i.serialize for i in events])


@app.route('/domains/<int:domID>/events/<int:eventsID>.json')
def eventJSON(domID, eventID):
    domevent = session.query(event).filter_by(domID=domID, eventID=eventID).one()
    return jsonify(event=domevent.serialize)


# # ATOM APIs to view domain and event Information
@app.route('/domains/xml', methods=['GET', 'POST'])
def domainsXML():
    domains = session.query(domain).all()
    return render_template('domains.xml', domains=domains)


# @app.route('/domains/<int:domID>/events.xml')
# def domeventsXML(domID):
#     dom = session.query(domain).filter_by(domID=domID).one()
#     events = session.query(event).filter_by(domID=domID).all()
#     domainsXML = dict2xml(jsonify(jsonify(events=[i.serialize for i in events]), wrap="domeventsXML")
#     response=make_response(xml)
#     response.headers['Content-Type']='application/atom+xml'
#     return response



# Show all domains
@app.route('/domains/', methods=['GET', 'POST'])
def domains():
    session.rollback()
    dom = session.query(domain).all()
    if 'username' not in login_session:
        return render_template('domains.html', domain=dom)
    else:
        return render_template('domains.html', domain=dom, logged_in=True)


# CRUD functions for domains
@app.route('/domains/new/', methods=['GET', 'POST'])
def newDom():
    if 'username' not in login_session:
        return redirect('/login')
    session.rollback()
    if request.method == 'POST':
        newdom = domain(name=request.form['name'], userID=login_session['user_id'])
        session.add(newdom)
        session.commit()
        flash("New domain created!")
        return redirect(url_for('domains'))
    else:
        return render_template('domainsnew.html', domain=domain)
        

@app.route('/domains/<int:domID>/edit/', methods=['GET', 'POST'])
def editDom(domID):
    if 'username' not in login_session:
        return redirect('/login')
    session.rollback()
    domToEdit = session.query(domain).filter_by(domID=domID).one()
    if request.method == 'POST':
        if request.form['name']:
            domToEdit.name = request.form['name']
        session.add(domToEdit)
        session.commit()
        return redirect(url_for('domevents', domID=domID))
    else:
        return render_template('domainsedit.html', domain=domToEdit)


@app.route('/domains/<int:domID>/delete/', methods=['GET', 'POST'])
def deleteDom(domID):
    if 'username' not in login_session:
        return redirect('/login')
    session.rollback()
    domToDelete = session.query(domain).filter_by(domID=domID).one()
    if request.method == 'POST':
        session.delete(domToDelete)
        session.commit()
        flash("domain deleted!")
        return redirect(url_for('domains'))
    else:
        return render_template('domainsdelete.html', domain=domToDelete)

# List all the events associated with a domain
@app.route('/domains/<int:domID>/', methods=['GET', 'POST'])
@app.route('/domains/<int:domID>/events/', methods=['GET', 'POST'])
def domevents(domID):
    dom = session.query(domain).filter_by(domID=domID).one()
    events = session.query(event).filter_by(domID=domID).all()
    creator = getUserInfo(dom.userID)
    if 'username' not in login_session or creator.userID != login_session['user_id']:
        return render_template('stars.html', domain=dom, events=events,
                               creator=creator)
    else:
        return render_template('stars.html', domain=dom, events=events,
                               creator=creator, logged_in=True)


# CRUD functions for events
@app.route('/domains/<int:domID>/new', methods=['GET', 'POST'])
def newevent(domID):
    if 'username' not in login_session:
        return redirect('/login')
    session.rollback()
    dom = session.query(domain).filter_by(domID=domID).one()
    if request.method == 'POST':
        newevent = event(name=request.form['name'], stars=request.form['stars'],
                       description=request.form['description'],
                       category=request.form['category'], domID=domID,
                       userID=login_session['user_id'], 
                       thumbnail_url=request.form['thumbnail_url'])
        session.add(newevent)
        session.commit()
        flash("New event created!")
        return redirect(url_for('domevents', domID=domID))
    else:
        return render_template('starsnew.html', domain=dom, domID=domID)


@app.route('/domains/<int:domID>/events/<int:eventID>/edit/', methods=['GET', 'POST'])
def editevent(domID, eventID):
    if 'username' not in login_session:
        return redirect('/login')
    dom = session.query(domain).filter_by(domID=domID).one()
    eventToEdit = session.query(event).filter_by(eventID=eventID).one()
    if request.method == 'POST':
        if request.form['name']:
            eventToEdit.name = request.form['name']
        if request.form['stars']:
            eventToEdit.stars = request.form['stars']
        if request.form['description']:
            eventToEdit.description = request.form['description']
        if request.form['category']:
            eventToEdit.category = request.form['category']
        session.add(eventToEdit)
        session.commit()
        return redirect(url_for('domevents', domID=domID))
    else:
        return render_template('starsedit.html', domain=dom, event=eventToEdit)


# Create a route for deleteMenuevent function here
@app.route('/domains/<int:domID>/events/<int:eventID>/delete/',
            methods=['GET', 'POST'])
def deleteevent(domID, eventID):
    if 'username' not in login_session:
        return redirect('/login')
    dom = session.query(domain).filter_by(domID=domID).one()
    eventToDelete = session.query(event).filter_by(domID=domID,
                                                 eventID=eventID).one()
    if request.method == 'POST':
        session.delete(eventToDelete)
        session.commit()
        return redirect(url_for('domevents', domID=domID))
    else:
        return render_template('starsdelete.html', domain=dom,
                               event=eventToDelete)

# helper routes
@app.route('/source')
def source():
    """ redirects to github repository """
    return redirect(repo_uri)

# if statement ensures script only runs if executed
# directly from the python interpreter (not used as imported module)
if __name__ == '__main__':
    # flash uses a secret key to create sessions for a user
    app.secret_key = 'super_secret_key'
    # reload server when a code change occurs, provides debugger in browser
    app.debug = True
    # runs local server with this application
    # the ''0.0.0.0' makes the server
    # publicly available in order to use vagrant
    app.run(host='0.0.0.0', port=5000)