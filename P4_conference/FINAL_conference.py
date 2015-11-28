# final app additions

# Task 1:

Add Endpoints methods

def _copySessionToForm(self, sesh, websafeConferenceKey): # TODO 1 is it suppose to take a websafekey arg?
    """Copy relevant fields from Session to SessionForm."""
    sf = SessionForm()
    for field in sf.all_fields():
        if hasattr(sesh, field.name):
            # convert Date to date string; just copy others
            if field.name.endswith('Date'):
                setattr(sf, field.name, str(getattr(sesh, field.name)))
            else:
                setattr(sf, field.name, getattr(sesh, field.name))
        elif field.name == "websafeConferenceKey":
            setattr(sf, field.name, conf.key.urlsafe())
    if websafeConferenceKey:
        setattr(sf, 'conference', websafeConferenceKey)
    sf.check_initialized()
    return cf

def _createSession(self, request):
""" -- open only to the organizer of the conference"""
    # preload necessary data items
    # ensure user = organizer of the conference
    user = endpoints.get_current_user()
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')
    user_id = getUserId(user)

    if not request.name:
        raise endpoints.BadRequestException("Conference 'name' field required")

    # fetch existing conference
    conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()

    # copy SessionForm/ProtoRPC Message into dict
    data = {field.name: getattr(request, field.name) for field in request.all_fields()}
    # del data['websafeConferenceKey']

    # add default values for those missing (both data model & outbound Message)
    for df in DEFAULTS:
        if data[df] in (None, []):
            data[df] = DEFAULTS[df]
            setattr(request, df, DEFAULTS[df])
    # convert dates from strings to Date objects; set month based on start_date
    if data['date']:
        data['date'] = datetime.strptime(data['date'][:10], "%Y-%m-%d").date()
        data['month'] = data['date'].month
    else:
        data['month'] = 0


    # generate Session Key based on user ID and Conference name
    # ID based on Profile key get Conference key from ID
    c_key = ndb.Key(Conference, conf.key.id())
    s_id = Session.allocate_ids(size=1, parent=c_key)[0]
    s_key = ndb.Key(Session, s_key, parent=c_key)

    data['key'] = c_key
    data['organizerUserId'] = request.organizerUserId = user_id

    Session(**data).put()

    # check to see if speaker exists in other sections, add to memcache if so

    return ""

def _copySessionToForm(self, sesh):
    """Copy relevant fields from Session to SessionForm."""
    sf = SessionForm()
    for field in sf.all_fields():
        if hasattr(sesh, field.name):
            # convert Time and Date to date string; just copy others
            if field.name in ['startTime', 'date']:
                setattr(sf, field.name, str(getattr(sesh, field.name)))
            else:
                setattr(sf, field.name, getattr(sesh, field.name))
        elif field.name == "websafeKey":
            setattr(cf, field.name, conf.key.urlsafe())
    sf.check_initialized()
    return sf


@endpoints.method(SessionForm, SessionForm, path='sessions',
        http_method='POST', name='createSession')
def createSession(self, request):
    """Create new Session in Conference."""
    return self._createSession(request)




@endpoints.method(SESSION_GET_REQUEST, SessionForms, path='session/{websafeConferenceKey}',
        http_method='GET', name='getConferenceSessions')
def getConferenceSessions(self, request):
    """Return requested sessions (by websafeConferenceKey)."""
    # make a query object for a specific ancestor
    seshs = Session.query(ancestor=ndb.Key(Conference, websafeConferenceKey)

    # return SessionForms
    return SessionForms(
        items=[self._copySessionToForm(seshs, getattr(prof, 'displayName'))


    data = {field.name: getattr(request, field.name) for field in request.all_fields()}
    # get Conference object from request; bail if not found
    conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
    if not conf:
        raise endpoints.NotFoundException(
            'No conference found with key: %s' % request.websafeConferenceKey)
    
    sesh = [(ndb.Key(Profile, conf.organizerUserId)) for session in conferences]
    prof = ndb.get_multi(organisers)

    prof = conf.key.parent().get()





@endpoints.method(SESSION_GET_REQUEST, SessionForms, path='sessions/{websafeConferenceKey}/{typeOfSession}',
        http_method='GET', name='getConferenceSessionsByType')
def getConferenceSessionsByType(websafeConferenceKey, typeOfSession):
"""Given a conference, return all sessions of a specified type (eg lecture, keynote, workshop)"""

    q = Session.query()
    return q.filter(Session.typeOfSession == typeOfSession)

    return SessionForms(items=[self._copySessionToForm(sesh, "")])






@endpoints.method(SPEAKER_GET_REQUEST, SessionForms, path='sessions/{speaker}',
        http_method='GET', name='getSessionsBySpeaker')
def getSessionsBySpeaker(speaker):
    #filter by property, returns all sessions by a particular speaker, across all conferences
    q = Session.query()
    return q.filter(Session.speaker == speaker)



# Explain in a couple of paragraphs your design choices for session and speaker implementation.
didn't create speaker as separate object, kept as a property (or create user as new attendee/user 
bc helps with headcount and ensures all people in central store. e.g. if you need comprehensive user list for administrative purposes)









# Task 2: Add Sessions to User Wishlist


Users should be able to mark some sessions that they are interested in 
and retrieve their own current wishlist. You are free to design the way this wishlist is stored.


def addSessionToWishlist(SessionKey):
 # -- adds the session to the user's list of sessions they are interested in attending

decide if they can only add conference they have registered to attend or if the wishlist is open to all conferences.

def getSessionsInWishlist():
 """queries for all the sessions in a conference that the user is interested in"""













#should these be in the conference.py file?

# Task 3: Work on indexes and queries

Create indexes

Make sure the indexes support the type of queries required by the new Endpoints methods.
Come up with 2 additional queries

Think about other types of queries that would be useful for this application. 
Describe the purpose of 2 new queries and write the code that would perform them.

Solve query related problem :
You don't like workshops and you don't like sessions after 7 pm. 
How would you handle a query for all non-workshop sessions before 7 pm? 
What is the problem for implementing this query? What ways to solve it did you think of?











"""Task 4: Add a Task
When a new session is added to a conference, check the speaker. 
If there is more than one session by this speaker at this conference, 
also add a new Memcache entry that features the speaker and session names. 
You can choose the Memcache key. The logic should be handled using App Engine's Task Queue."""

#in app.yaml
# Task 4
- url: /tasks/cache_sessions
  script: main.app
  login: admin


EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID


    # @staticmethod
    # def cacheSessions():
    #     """Create cache_sessions; used by
    #     memcache cron job & putCachedSessions().
    #     """
    #     confs = Conference.query(ndb.AND(
    #         Conference.seatsAvailable <= 5,
    #         Conference.seatsAvailable > 0)
    #     ).fetch(projection=[Conference.name])    

    #    if confs:
    #    		# If there are almost
    #    		announcement = '%s %s %'


MEMCACHE_SESSIONS_KEY = "SPEAKER_SESSIONS"
SESSIONS_TPL = 

add to : def createSession(SessionForm, websafeConferenceKey):

# check if speaker exists in other sessions; if so, add list of all sessions with associated speakerto memcache
	sessions = Session.query(Session.speaker == data['speaker'],
	    ancestor=p_key) # TODO why ancestor=p_key??? all attributed to one conference? speaker[conference][session]??
	if len(list(sessions)) > 1: #find a different expression?
# add a new Memcache entry that features the speaker and session names
		to_cache = {}
		to_cache['speaker'] = data['speaker']
		to_cache['sessionNames'] = [session.name for session in sessions]
        memcache.set(MEMCACHE_SESSIONS_KEY, to_cache)

        if not memcache.set(MEMCACHE_SESSIONS_KEY, to_cache):
            logging.error('Memcache set failed.')
      
    	taskqueue.add(params={'speaker': speaker.name(),
        'sessions': repr(request)}, # TODO add logic that iterates through the sessions
        url='/tasks/cache_sessions'
 
        )

def getFeaturedSpeaker():


# git commits
# Add url handler cache_sessions to app.yaml
# Add HTTP controller handler for memcache & task queue access in main.py


