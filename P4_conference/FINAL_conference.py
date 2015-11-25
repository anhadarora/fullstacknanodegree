# final app additions

# Task 1:

Add Endpoints methods

def getConferenceSessions(websafeConferenceKey):
 """Given a conference, return all sessions"""
 return allsessions

def getConferenceSessionsByType(websafeConferenceKey, typeOfSession):
 Given a conference, return all sessions of a specified type (eg lecture, keynote, workshop)

def getSessionsBySpeaker(speaker):
 Given a speaker, return all sessions given by this particular speaker, across all conferences

def createSession(SessionForm, websafeConferenceKey):
 -- open only to the organizer of the conference





# Explain in a couple of paragraphs your design choices for session and speaker implementation.











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


