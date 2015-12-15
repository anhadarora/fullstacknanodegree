def gconnect():
    """ Handles the Google+ sign-in process on the server side.
    Server side function to handle the state-token and the one-time-code
    send from the client callback function following the seven steps of the
    Google+ sign-in flow. See the illustrated flow on
    https://developers.google.com/+/web/signin/server-side-flow.
    Returns:
        When the sign-in was successful, a html response is sent to the client
        signInCallback-function confirming the login. Otherwise, one of the
        following responses is returned:
        200 OK: The user is already connected.
        401 Unauthorized: There is either a mismatch between the sent and
            received state token, the received access token doesn't belong to
            the intended user or the received client id doesn't match the web
            apps client id.
        500 Internal server error: The access token inside the received
            credentials object is not a valid one.
    Raises:
        FlowExchangeError: The exchange of the one-time code for the
            credentials object failed.
    """
    # Confirm that the token the client sends to the server matches the
    # state token that the server sends to the client.
    # This roundship verification helps ensure that the user is making the
    # request and and not a maliciousscript.
    # Using the request.args.get-method, the code examines the state token
    # passed in and domares it to the state of the login session. If thesse
    # two do not match, a response message of an invalid state token is created
    # and returned to the client. No further authentication will occur on the
    # server side if there was a mismatch between these state token.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If the above statement is not true then I can proceed and collect the
    # one-time code from the server with the request.data-function.
    code = request.data

    # 5) The Server tries to exchange the one-time code for an access_token and
    # an id_token (credentials object).
    # 6) When successful, Google returns the credentials object. Then the
    # server is able to make its own API calls, which can be done while the
    # user is offline.
    try:
        # Create an oauth_flow object and add clients secret key information
        # to it.
        oauth_flow = flow_from_clientsecrets(
            'g_client_secrets.json', scope='')
        # Postmessage specifies that this is the one-time-code flow that my
        # server will be sending off.
        oauth_flow.redirect_uri = 'postmessage'
        # The exchange is initiated with the step2_exchange-function passing in
        # the one-time code as input.
        # The step2_exchange-function of the flow-class exchanges an
        # authorization (one-time) code for an credentials object.
        # If all goes well, the response from Google will be an object which
        # is stored under the name credentials.
        credentials = oauth_flow.step2_exchange(code)
    # If an error happens along the way, then this FlowExchangeError is thrown
    # and sends the response as an JSON-object.
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # After the credentials object has been received. It has to be checked if
    # there is a valid access token inside of it.
    access_token = credentials.access_token
    # If the token is appended to the following url, the Google API server can
    # verify that this is a valid token for use.
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Create a JSON get-request containing the url and access-token and store
    # the result of this request in a variable called result
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, send a 500 internal
    # server error is send to the client.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # If the above if-statement isn't true then the access token is working.

    # Next, verify that the access token is used for the intended user.
    # Grab the id of the token in my credentials object and domare it to the
    # id returned by the google api server. If these two ids do not match, then
    # I do not have the correct token and should return an error.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Similary, if the client ids do not match, then my app is trying to use a
    # client_id that doesn't belong to it. So I shouldn't allow for this.
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the user is already logged in
    # ! Credentials shouldn't been stored in the session
    # stored_credentials = login_session.get('credentials')
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    # So assuming that none of these if-statements were true, I have a valid
    # access token and my user is successfully able to login to my server.
    # In this user's login_session, the credentials and the gplus_id are stored
    # to recall later (see check above).
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Use the google plus API to get some more information about the user.
    # Here, a message is send off to the google API server with the access
    # token requesting the user info allowed by the token scope and store it in
    # an object called data.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    # Data should have all of the values listed on
    # https://developers.google.com/+/api/openidconnect/getOpenIdConnect#response
    # filled in, so long as the user specified them in their account. In the
    # following, the users name, picture and e-mail address are stored in the
    # login session.
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # If user doesn't exist, make a new one.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # 7) If the above worked, a html response is returned confirming the login
    # to the Client.
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("You are now logged in as %s" % login_session['username'])
    return output
