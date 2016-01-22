# final app additions

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
                return redirect(url_for('login', next=request.url))
    return decorated_function

# and one line above each function where users need to be logged in, place this code:
@login_required
def XXXfunction(args):
    XXXcode
# ref : flask.pocoo.org/docs/0.10/patterns/viewdecorators/

# Task 1 - added to conference.py

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

    # Task 4 TODO: check to see if speaker exists in other sections, add to memcache if so

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

The speaker was not created as separate object, kept as a property (or create user as new attendee/user 
bc helps with headcount and ensures all people in central store. 
(e.g. if you need comprehensive user list for administrative purposes)

created sessions as a separate 'kind' object to store different entities with speaker as a property?

and sessions as a property of user profile
"""




"""# Task 2: Add Sessions to User Wishlist 

Users should be able to mark some sessions that they are interested in 
and retrieve their own current wishlist. You are free to design the way this wishlist is stored.

chose to store as user profile property and to add sessions for conference not registered for. 
this could allow for targeting marketing for prospective conf attendees.ctive conference attendees."""



# pretty much done need to test 

@endpoints.method(WISHLIST_POST_REQUEST, StringMessage,
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
    sessKey = request.websafeSessionKey

    # query by user key as the ancestor
    prof = p_key.get()

    if prof and prof.sessKeyWishlist:
        prof.sessKeyWishlist.append(sessKey)
    else:
        raise endpoints.NotFoundException('Registration required')
    prof.put()



# done...need to test and understand forms

@endpoints.method(message_types.VoidMessage, SessionForms,
                  path='conference/session/wishlist/get',
                  http_method='GET',
                  name='getSessionsFromWishlist')
def getSessionsFromWishlist(self, request):
    """Get Sessions from current user wishlist"""
    # preload necessary data items
    user = endpoints.get_current_user()
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')

    # get profile and wishlist
    prof = self._getProfileFromUser()
    sessKeys = user.sessKeyWishlist
    wishlist = [sessKey.get() for sessKey in sessKeys]

    # return the wishlist
    return SessionForms(
        items=[self._copySessionToForm(sessKey) for sessKey in wishlist]






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
You can choose the Memcache key. The logic should be handled using App Engine's Task Queue.
reqs: student uses app egines task queue when implem the featured speaker logic"""

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

add to : 

def createSession(SessionForm, websafeConferenceKey):

# check if speaker exists in other sessions; if so, add list of all sessions with associated speaker to memcache
	sessions = Session.query(Session.speaker == data['speaker'],
	    ancestor=p_key) # TODO why ancestor=p_key??? all attributed to one conference? speaker[conference][session]??
	if len(list(sessions)) > 1: 

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



# <------------OR USE------------> (https://github.com/TomTheToad/FullStack_Udacity_P4/blob/master/conference.py)

# Update featured speaker key in memcache
# get current speaker
    speaker = session.speakerDisplayName

# get the number of sessions hosted by current speaker
    number_sessions = self._getNumber of ConferenceSessionBySpeaker(speaker, request.websafeConferenceKey)

    # if number of sessions greater than one set featured speaker
    if number_sessions > 1:
        taskqueue.add(
            params={'speaker': speaker,
                    'websafeConferenceKey': request.websafeConferenceKey' },
                    url = '/tasks/set_featured_speaker')

# <------------OR USE------------>  https://github.com/sshebel/fullstack_proj4/blob/master/conference.py

        # if speaker is presenting 2 or more sessions
        # add a task to check if this speaker is now a featured speaker
        if count >= 2:             
            taskqueue.add(params={'conference': c_key.urlsafe(),'speaker':data['speaker']},url='/tasks/featuredSpeaker')
        #send email to creator
        taskqueue.add(params={'email': user.email(),
            'sessionInfo': repr(request)},
            url='/tasks/send_confirmation_email'
        )








# allanbreyes

def getFeaturedSpeaker(self, request):
    """Returns the session for the featured speaker"""
    # pull data out of memcache
    data = memcache.get('featured_speaker')
    from pprint import pprint
    pprint(data)
    sessions = []
    sessionNames = []
    speaker = None

    if data and data.has_key('speaker') and data.has_key('sessionNames'):
        speaker = data['speaker']
        sessionNames = data['sessionNames']

    # if memcache fails or is empty, pull speaker from upcoming session

else:
    upcoming_session = Session.query(Session.date >= datetime.now())\
                            .order(Session.date, Session.startTime).get()
    if upcoming_session:
        speaker = upcoming_session.speakersessions = Session.query(Session.speaker ==speaker)
        sessionNames = [session.name for session in sessions]
        
# populate speaker form
sf = SpeakerForm()
for field in sf.all_fields():
    if field.name == 'sessionNames':
        setattr(sf, field,name, sessionNames)
    elif field.name == 'speaker':
        setattr(sf, field,name, speaker)
sf.check_initialized()

return sf




# Add url handler cache_sessions to app.yaml
# Add HTTP controller handler for memcache & task queue access in main.py












# <------------OR USE------------> (https://github.com/TomTheToad/FullStack_Udacity_P4/blob/master/conference.py)

def _setFeaturedSpeaker(self, featured_speaker, websafeConferenceKey):

    #set Memcache key to featured speaker
    MEMCACHE_SPEAKER_KEY = 'FEATURED SPEAKER'

    # get session names associated with featured speaker
    sessions = Session.query(
        ancestor = (ndb.Key(urlsafe=websafeConferenceKey)))
    sessions.filter(Session.speakerDisplayName == featured_speaker)

    # Create message
    memcache_msg = "Our Featured speaker is " + str(featured_speaker) + \
                   ". sessions: "

    for session in sessions:
        memcache_msg += str(session.name) + ", "

    # Set memcache key
    memcache.set(memcache_speaker_key, memcache_msg)

@endpoints.method(message_types.VoidMessage, StringMessage,
                  path='conference/featured_speaker/get',
                  http_method='GET',
                  name='getFeaturedSpeaker')
def getFeaturedSpeaker(self, request):
    """Get featured speaker"""
    memcache_speaker = memcache.get('FEATURED SPEAKER')

    if memcache_speaker is not None:
        return StringMessage(data=memcache_speaker)
    else:
        msg = "Check back for our upcoming featured speaker!"
        return StringMessage(data=msg)



# <------------OR USE------------>  https://github.com/sshebel/fullstack_proj4/blob/master/conference.py

@staticmethod
def _cacheFeaturedSpeaker(c_urlsafeKey,speaker_id):
    """ Cache a featured speaker and associated sessions for a conference
        Called from getFeaturedSpeaker and CreateFeaturedSpeaker(from the task queue)
    """
    logging.info("speaker id=%s"%speaker_id)
    c_key = ndb.Key(urlsafe=c_urlsafeKey)
    sessionlist = Session.query(ancestor=c_key).fetch()
    memstring=""
    featuredsessions=[]
    for session in sessionlist:
        if session.speaker == speaker_id:
                featuredsessions.append(session.name)
    memstring = 'Featured speaker,%s, will be leading the following sessions %s' % (
        ndb.Key(Speaker,speaker_id).get().displayName,
        ', '.join(featuredsessions))
    if memstring:
        memcache.set("featuredspeaker-%s"%c_urlsafeKey,memstring)
    return(memstring)


@endpoints.method(GET_REQUEST, StringMessage,
        path='featuredSpeaker/{websafeKey}',
        http_method='GET', name='getFeaturedSpeaker')
def getFeaturedSpeaker(self, request):
    """ Get the featured speaker info for the specified conference from memcache """
    c_key = ndb.Key(urlsafe=request.websafeKey)
    fspeaker = memcache.get("featuredspeaker-%s"%request.websafeKey)
    return StringMessage(data=fspeaker)



