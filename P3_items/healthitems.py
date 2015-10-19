from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
# setup module for authorization and authentication, login_session works like a dictionary
from flask import session as login_session
import random, string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, company, item, user
# create a flow object from the client's secret JSON file, which stores clientID, client secret, and oAuth parameters
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
# json module provides an API for converting in memory python objects to a serialized representation (json)
import json
# converts the return value from a function into a real response object that we can send off to our client
from flask import make_response
import requests

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Health Items App"

app = Flask(__name__)

engine = create_engine('sqlite:///healthitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# decorator will call function that follows it whenever the web server receives request with url that matches the arguent
# Create anti-forgery state token
@app.route('/login', methods=['GET', 'POST'])
def showLogin():
 	  # create a random anti-forgery state token with each GET request sent to the 5000/login 
	state = ''.join(random.choice(string.ascii_uppercase + string.
		digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', state=state)

# SERVER SIDE FUNCTION FOR LOGGING IN
@app.route('/gconnect/', methods=['POST'])
def gconnect():
	  # confirm that the token the client sends to the server is the same as the token the server sends to the client
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
	
	 # check that the access token is valid
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
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'

	 # Store the access token in the session for later use
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	 # Get user info from Google API
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width:300px; height:300px; border-radius:150px; -webkit-border-radius:150px; -moz-border-radius:150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

 # DISCONNECT = revoke a current user's token and reset their login_session
@app.route('/gdisconnect/')
def gdisconnect():
	 # Only disconnect a connected user.
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	 # Execute HTTP GET request to revoke current token.
	access_token = credentials.access_token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	if result['status'] == '200':
		# Reset the user's session.
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps())
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		# for whatever reason, the given token was invalid.
		response = make_response(
			json.dumps('Failed to revoke token for given user.'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response

# JSON APIs to view Company Information

# @app.route('/company/<int:compID>/item/JSON')
# def compItemsJSON(compID):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return jsonify(MenuItems=[i.serialize for i in items])


# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
# def itemJSON(restaurant_id, menu_id):
#     Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
#     return jsonify(Menu_Item=Menu_Item.serialize)


# @app.route('/restaurant/JSON')
# def restaurantsJSON():
#     restaurants = session.query(Restaurant).all()
#     return jsonify(restaurants=[r.serialize for r in restaurants])


# Show all companies

@app.route('/companies/', methods=['GET', 'POST'])
def companies():
	session.rollback()
	comp = session.query(company).all()
	return render_template('companies.html', company=comp)          

@app.route('/companies/new/', methods=['GET', 'POST'])
def newComp():
	if 'username' not in login_session:
		return redirect('/login')
	session.rollback()
	if request.method == 'POST':
		newComp = company(name = request.form['name'], userID = login_session['userID'])
		session.add(newComp)
		session.commit()
		flash("New company created!")
		return redirect(url_for('companies'))
	else:
		return render_template('newComp.html')

@app.route('/companies/<int:compID>/edit/', 
			methods=['GET', 'POST'])
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
		return render_template('editComp.html', company=comp, item=itemToEdit)

# Task 3: Create a route for deleteMenuItem function here

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

@app.route('/companies/<int:compID>/', methods=['GET', 'POST'])
@app.route('/companies/<int:compID>/items/', methods=['GET', 'POST'])
def compItems(compID):
	comp = session.query(company).filter_by(compID=compID).one()
	items = session.query(item).filter_by(compID=compID).all()
	return render_template('items.html', company=comp, items=items)

@app.route('/companies/<int:compID>/new', methods=['GET', 'POST'])
def newItem(compID):
	if 'username' not in login_session:
		return redirect('/login')
	comp = session.query(company).filter_by(compID=compID).one()
	if request.method == 'POST':
		newItem = item(name = request.form['name'], price = request.form['price'], 
						description = request.form['description'], 
						category = request.form['category'], compID=compID,
						userID = company.userID)
		session.add(newItem)
		session.commit()
		flash("New item created!")
		return redirect(url_for('compItems', compID=compID))
	else:
		return render_template('newItem.html', company=comp)
	   

# Task 2: Create route for editMenuItem function here, need to provide methods arguement in the decorator to respond to POST requests too

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
		session.add(itemToEdit)
		session.commit()
		return redirect(url_for('compItems', compID=compID))
	else:
		return render_template('editItem.html', company=comp, item=itemToEdit)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/companies/<int:compID>/items/<int:itemID>/delete/', 
			methods=['GET', 'POST'])
def deleteItem(compID, itemID):
	if 'username' not in login_session:
		return redirect('/login')
	comp = session.query(company).filter_by(compID=compID).one()
	itemToDelete = session.query(item).filter_by(compID=compID, itemID=itemID).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('compItems', compID=compID))
	else:
		return render_template('deleteItem.html', company=comp, item=itemToDelete)



# Create a new user by extracting all the necessary data from the login_session
def createUser(login_session):
	newUser = user(name = login_session['username'], email = login_session['email'], 
		picture = login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(user).filter_by(email = login_session['email']).one()
	return user.userID

def getUserInfo(userID):
	return session.query(user).filter_by(userID = userID).one()

def getUserID(email):
	try:
		user = session.query(user).filter_by(email = email).one()
		return user.userID
	except:
		return None


# if statement ensures script only runs if executed
# directly from the python interpreter (not used as imported module)
if __name__ == '__main__':
	# flash uses a secret key to create sessions for a user
	app.secret_key = 'super_secret_key'
	# reloads server each time it notices a code change and provides debugger in browser
	app.debug = True
	# runs local server with this application
	# the ''0.0.0.0' makes the server 
	# publicly available in order to use vagrant 
	app.run(host = '0.0.0.0', port = 5000)
