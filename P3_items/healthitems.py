from flask import Flask, render_template, request, \
    redirect, url_for, flash, jsonify
# import module for authorization/authentication
from flask import session as login_session
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, company, item, user
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
APPLICATION_NAME = "Healthitems App"

app = Flask(__name__)

engine = create_engine('sqlite:///healthitemswithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
        return redirect(url_for('companies'))
    else:
        flash("You were not logged in")
        return redirect(url_for('companies'))


# JSON APIs to view Company and Item Information
@app.route('/companies.json')
def companiesJSON():
    companies = session.query(company).all()
    return jsonify(Companies=[c.serialize for c in companies])


@app.route('/companies/<int:compID>/items.json')
def compItemsJSON(compID):
    comp = session.query(company).filter_by(compID=compID).one()
    items = session.query(item).filter_by(compID=compID).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/companies/<int:compID>/items/<int:itemsID>.json')
def itemJSON(compID, itemID):
    compItem = session.query(item).filter_by(compID=compID, itemID=itemID).one()
    return jsonify(Item=compItem.serialize)


# # ATOM APIs to view Company and Item Information
# @app.route('/companies.xml')
# def companiesXML():
#     companies = session.query(company).all()
#     companiesXML = dict2xml(jsonify(Companies=[c.serialize for c in companies]), wrap="companiesXML")
#     response = make_response(xml)
#     response.headers['Content-Type'] = 'application/xml'
#     return response


# @app.route('/companies/<int:compID>/items.xml')
# def compItemsXML(compID):
#     comp = session.query(company).filter_by(compID=compID).one()
#     items = session.query(item).filter_by(compID=compID).all()
#     companiesXML = dict2xml(jsonify(jsonify(Items=[i.serialize for i in items]), wrap="compItemsXML")
#     response=make_response(xml)
#     response.headers['Content-Type']='application/xml'
#     return response


# Show all companies
@app.route('/companies/', methods=['GET', 'POST'])
def companies():
    session.rollback()
    comp = session.query(company).all()
    if 'username' not in login_session:
        return render_template('publicCompanies.html', company=comp)
    else:
        return render_template('companies.html', company=comp)


# CRUD functions for companies
@app.route('/companies/new/', methods=['GET', 'POST'])
def newComp():
    if 'username' not in login_session:
        return redirect('/login')
    session.rollback()
    if request.method == 'POST':
        newComp = company(name=request.form['name'], userID=login_session['user_id'])
        session.add(newComp)
        session.commit()
        flash("New company created!")
        return redirect(url_for('companies'))
    else:
        return render_template('newComp.html')


@app.route('/companies/<int:compID>/edit/', methods=['GET', 'POST'])
def editComp(compID):
    if 'username' not in login_session:
        return redirect('/login')
    session.rollback()
    compToEdit = session.query(company).filter_by(compID=compID).one()
    if request.method == 'POST':
        if request.form['name']:
            compToEdit.name = request.form['name']
        session.add(compToEdit)
        session.commit()
        return redirect(url_for('compItems', compID=compID))
    else:
        return render_template('editComp.html', company=compToEdit)


@app.route('/companies/<int:compID>/delete/', methods=['GET', 'POST'])
def deleteComp(compID):
    if 'username' not in login_session:
        return redirect('/login')
    session.rollback()
    compToDelete = session.query(company).filter_by(compID=compID).one()
    if request.method == 'POST':
        session.delete(compToDelete)
        session.commit()
        flash("company deleted!")
        return redirect(url_for('companies'))
    else:
        return render_template('deleteComp.html', company=compToDelete)

# List all the items associated with a company
@app.route('/companies/<int:compID>/', methods=['GET', 'POST'])
@app.route('/companies/<int:compID>/items/', methods=['GET', 'POST'])
def compItems(compID):
    comp = session.query(company).filter_by(compID=compID).one()
    items = session.query(item).filter_by(compID=compID).all()
    creator = getUserInfo(comp.userID)
    if 'username' not in login_session or creator.userID != login_session['user_id']:
        return render_template('publicItems.html', company=comp, items=items,
                               creator=creator)
    else:
        return render_template('items.html', company=comp, items=items,
                               creator=creator)


# CRUD functions for items
@app.route('/companies/<int:compID>/new', methods=['GET', 'POST'])
def newItem(compID):
    if 'username' not in login_session:
        return redirect('/login')
    comp = session.query(company).filter_by(compID=compID).one()

    if request.method == 'POST':
        newItem = item(name=request.form['name'], price=request.form['price'],
                       description=request.form['description'],
                       category=request.form['category'], compID=compID,
                       userID=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect(url_for('compItems', compID=compID))
    else:
        return render_template('newItem.html', company=comp)


@app.route('/companies/<int:compID>/items/<int:itemID>/edit/', methods=['GET', 'POST'])
def editItem(compID, itemID):
    if 'username' not in login_session:
        return redirect('/login')
    comp = session.query(company).filter_by(compID=compID).one()
    itemToEdit = session.query(item).filter_by(itemID=itemID).one()
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['price']:
            itemToEdit.price = request.form['price']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        if request.form['category']:
            itemToEdit.category = request.form['category']
        session.add(itemToEdit)
        session.commit()
        return redirect(url_for('compItems', compID=compID))
    else:
        return render_template('editItem.html', company=comp, item=itemToEdit)


# Create a route for deleteMenuItem function here
@app.route('/companies/<int:compID>/items/<int:itemID>/delete/',
            methods=['GET', 'POST'])
def deleteItem(compID, itemID):
    if 'username' not in login_session:
        return redirect('/login')
    comp = session.query(company).filter_by(compID=compID).one()
    itemToDelete = session.query(item).filter_by(compID=compID,
                                                 itemID=itemID).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('compItems', compID=compID))
    else:
        return render_template('deleteItem.html', company=comp,
                               item=itemToDelete)


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
