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


def _createSessionObject(self, request):
""" -- open only to the organizer of the conference"""
    # load necessary data items from the sess
    # copy SessionForm/ProtoRPC Message into dict
    data = {field.name: getattr(request, field.name) for field in request.all_fields()}
    # del data['websafeConferenceKey']
    # del data['organizerDisplayName']

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


    # generate Session Key based on Conference key and organizer(?)
    # ID based on Profile key get Conference key from ID
    c_key = ndb.Key(Conference, conf.key.id())
    s_id = Session.allocate_ids(size=1, parent=c_key)[0]
    s_key = ndb.Key(Session, s_key, parent=c_key)

    data['key'] = s_key
    data['organizerUserId'] = request.organizerUserId = user_id

    Session(**data).put()

    # check to see if speaker exists in other sections, add to memcache if so

    #return session form
    return self._copySessionToForm(s_key.get())


@endpoints.method(SessionForm, SessionForm, path='conference/{websafeConferenceKey}/createsession',
        http_method='POST', name='createSession')
def createSession(self, request):
    """Create new Session in Conference."""
    # fetch existing conference
    conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
    if not conf:
        raise endpoints.NotFoundException(
            'No conference found with key: %s' % request.websafeKey)

    #fetch user
    user = endpoints.get_current_user()
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')
    user_id = getUserId(user)

    # ensure user = organizer of the conference
    owner = conf.key.parent().id()
    if owner != user_id:
        raise endpoints.UnauthorizedException("User (%s) is not the owner of the conference (%s)"%(user_id,owner))
    if not request.name:
        raise endpoints.BadRequestException("Conference 'name' field required")


    return self._createSessionObject(request)
    # return self._createSessionObject(request,conf.key,conf.name,user)  # why???




@endpoints.method(message_types.VoidMessage, SessionForms, path='conference/{websafeConferenceKey}/sessions',
        http_method='POST', name='getConferenceSessions')
def getConferenceSessions(self, request):
    """Return requested sessions (by websafeConferenceKey)."""
    # make a query object for a specific ancestor
    c_key = ndb.Key(Conference, websafeConferenceKey).get()
    sessions = Session.query(ancestor=c_key)

    # get parent conference key and name
    conf = c_key.get()
    name = getattr(conf, 'name') #why?
    
    # return set of SessionForm objects per session
    return SessionForms(
        items=[self._copySessionToForm(sesh, websafeConferenceKey) 
                for sesh in sessions]




@endpoints.method(SESSION_GET_REQUEST, SessionForms, path='sessions/{websafeConferenceKey}/{typeOfSession}',
        http_method='GET', name='getConferenceSessionsByType')
def getConferenceSessionsByType(websafeConferenceKey, typeOfSession):
"""Given a conference, return all sessions of a specified type (eg lecture, keynote, workshop)"""

    q = Session.query()
    return q.filter(Session.typeOfSession == typeOfSession)

    return SessionForms(
        items=[self._copySessionToForm(sesh, websafeConferenceKey)
            for sesh in q])






@endpoints.method(SPEAKER_GET_REQUEST, SessionForms, path='sessions/{speaker}',
        http_method='GET', name='getSessionsBySpeaker')
def getSessionsBySpeaker(speaker):
    #filter by property, returns all sessions by a particular speaker, across all conferences
    q = Session.query()
    return q.filter(Session.speaker == speaker)

    return SessionForms(items=[self._copySessionToForm(sesh, websafeConferenceKey)] for sesh in q)


"""
Explain in a couple of paragraphs your design choices for session and speaker implementation.
didn't create speaker as separate object, kept as a property (or create user as new attendee/user 
bc helps with headcount and ensures all people in central store. 
(e.g. if you need comprehensive user list for administrative purposes)

created sessions as a separate 'kind' object to store different entities with speaker as a property?

and sessions as a property of user profile
"""







"""# Task 2: Add Sessions to User Wishlist


Users should be able to mark some sessions that they are interested in 
and retrieve their own current wishlist. You are free to design the way this wishlist is stored.
thought about putting as a user profile property, but not good bc of DB design rules, what if not all of them have a wishlist
one wishlist per conference"""



def _createWishlistObject(self):
    user = self._getProfileFromUser()
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')
    p_key = user.key

    wish_list = Wishlist(parent=p_key)
    wish_list.userID = user.mainEmail

    wish_list.put()

def _getSessionsInWishlist(self):
 """queries for all the sessions in a conference that the user is interested in"""

    user = self._getProfileFromUser()
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')
    p_key = user.key
    wish_list = Wishlist.query(ancestor=user.key).get() # put .get() after p_key = user.key instead?

    return SessionForms(
        items=[self._copySessionToForm(sesh, websafeConferenceKey)
            for sesh in wish_list])

# -OR-

#     forms = SessionForms()

#     for key in wishlist.sessionKeys:
#         query = Session.query(Session.key == key).get()
#         forms.items += [self._copySessionToForm(session=query)]

#     return forms



@endpoints.method(message_types.VoidMessage, SessionForms,
                  path='conference/session/wishlist/get',
                  http_method='GET',
                  name='getSessionsInWishlist')
def getSessionsInWishlist(self, request):
    """Get Session from current user wishlist"""
    return self._getSessionsInWishlist()


@endpoints.method(WishlistForm, StringMessage,
                  path='conference/{websafekey}/session/{websafeSessionKey}/wishlist/add', # necessarily want to add the websafekey and websadesessionkey in the url here??
                  http_method='POST',
                  name='addSessionToWishlist')
def addSessionToWishlist(self, request):
 # -- adds the session to the user's list of sessions they are interested in attending decided that wishlist is open to all conferences so user can use as a bookmarking function 

    user = self._getProfileFromUser()
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')
    p_key = user.key

    confKey = request.websafeKey
    SessionKey = request.websafeSessionKey

    # query by user key as the ancestor
    wish_list = Wishlist.query(ancestor=user.key).get() # do i need to have .get() at the end here?

    if wish_list and wish_list.s_keys:
        wish_list.s_keys.append(SessionKey) #where is this session key coming from?
    else:
        self._createWishlistObject(user)
        wish_list.c_key = [confKey]
        wish_list.s_keys = [SessionKey]
    wish_list.put()









#should these be in the conference.py file?

# Task 3: Work on indexes and queries

"""Create indexes

Make sure the indexes support the type of queries required by the new Endpoints methods.
Come up with 2 additional queries

Think about other types of queries that would be useful for this application. 
Describe the purpose of 2 new queries and write the code that would perform them."""


1. query other attendees of a conference (not query registeredconferences and list other attendees where other )
registeredusers of conference()


@endpoints.method(message_types.VoidMessage, ProfileFeedForms,
        path='conference/{websafeConferenceKey}/sociallist',
        http_method='POST', name='getSocialFeed')
def getSocialFeed(self, request):
    # fetch existing conference
    conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
    if not conf:
        raise endpoints.NotFoundException(
            'No conference found with key: %s' % request.websafeKey)

    #fetch user
    user = endpoints.get_current_user()
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')
    user_id = getUserId(user)

    # pull up other users of that conference
    profs = Profile.query()
    profs.filter(Profile.conferenceKeysToAttend == conf ))

    # return other users of that conference
    return ProfileForm(

    items=[self._copyConferenceToForm(conf, getattr(prof, 'displayName')) for conf in confs]
)

q.Profile.query().filter(Profile.conferenceKeysToAttend == conf)

class SocialForm(messages.Message):
    """ProfileFeedForm -- Profile Feed outbound form message"""
    displayName = messages.StringField(1)
    conferenceKeysToAttend = messages.StringField(2, repeated=True)

class SocialForms(messages.Message):
    """ConferenceForms -- multiple Conference outbound form message"""
    socialList = messages.MessageField(ConferenceForm, 1, repeated=True)


2. query all sessions by type, query past sessions?



3. What is the problem for implementing this query? What ways to solve it did you think of?

This query requires an inequality filter, and datastore only supports inequality filtering on a single property (not multiple properties)

@endpoints.method(SessionQueryForms, SessionForms, path='sessions/{websafeConferenceKey}/',
        http_method='GET', name='getConferenceSessionsByType')
def getConferenceSessionsByType(websafeConferenceKey, typeOfSession):
"""Given a conference, return all sessions of a specified type (eg lecture, keynote, workshop)"""

    q = Session.query()
    return q.filter(Session.typeOfSession != 'workshops' and Session.startTime <= 19:00)

    return SessionForms(
        items=[self._copySessionToForm(sesh, websafeConferenceKey)
            for sesh in q])


    def queryConferences(self, request):
        """Query for conferences."""
        conferences = self._getQuery(request)

        # need to fetch organiser displayName from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile, conf.organizerUserId)) for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return individual ConferenceForm object per Conference
        return ConferenceForms(
                items=[self._copyConferenceToForm(conf, names[conf.organizerUserId]) for conf in \
                conferences]
        )






















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


