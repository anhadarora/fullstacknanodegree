#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 wesc Exp wesc $

created by wesc on 2014 apr 21

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'


from datetime import datetime, timedelta, time as timed
import time

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import ConflictException
from models import Profile
from models import ProfileMiniForm
from models import ProfileForm
from models import StringMessage
from models import BooleanMessage
from models import Conference
from models import ConferenceForm
from models import ConferenceForms
from models import ConferenceQueryForm
from models import ConferenceQueryForms
from models import TeeShirtSize
from models import Session
from models import SessionForm
from models import SessionForms
from models import SessionQueryForm
from models import SessionQueryForms
from models import SocialForm
from models import SocialForms

from settings import WEB_CLIENT_ID
from settings import ANDROID_CLIENT_ID
from settings import IOS_CLIENT_ID
from settings import ANDROID_AUDIENCE

from utils import getUserId
import logging
logging.getLogger().setLevel(logging.DEBUG)


EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"
ANNOUNCEMENT_TPL = ('Last chance to attend! The following conferences '
                    'are nearly sold out: %s')
# Set MEMCACHE key to FEATURED SPEAKER
MEMCACHE_FEATURED_SPEAKER = "FEATURED_SPEAKER"
FEATURED_SPEAKER_TPL = ("Our featured speaker is %s. For sessions: ")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

DEFAULTS = {
    "city": "Default City",
    "maxAttendees": 0,
    "seatsAvailable": 0,
    "topics": [ "Default", "Topic" ],
}
SESHDEFAULTS = {
    "duration": 0,
    "highlights": [ "Default", "Highlights" ],
}
OPERATORS = {
            'EQ':   '=',
            'GT':   '>',
            'GTEQ': '>=',
            'LT':   '<',
            'LTEQ': '<=',
            'NE':   '!='
            }

FIELDS =    {
            'CITY': 'city',
            'TOPIC': 'topics',
            'MONTH': 'month',
            'MAX_ATTENDEES': 'maxAttendees',
            }

CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)

CONF_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    websafeConferenceKey=messages.StringField(1),
)

# in the midst of implementing
SESSIONFIELDS =    {
            'DATE': 'date',
            'TIME': 'time',
            'DURATION': 'duration',
            'LOCATION': 'location',
            'SEATSAVAILABLE': 'seatsavailable'
            }

SESSION_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1, required=True),
    typeOfSession=messages.StringField(2)
)

SESSION_POST_REQUEST = endpoints.ResourceContainer(
    SessionForm,
    websafeConferenceKey=messages.StringField(1, required=True),
)

WISH_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeSessionKey=messages.StringField(1),
)

WISH_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    websafeSessionKey=messages.StringField(1),
)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@endpoints.api(name='conference', version='v1', audiences=[ANDROID_AUDIENCE],
    allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID, ANDROID_CLIENT_ID, IOS_CLIENT_ID],
    scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""

# - - - Conference objects - - - - - - - - - - - - - - - - -

    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('Date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "websafeConferenceKey":
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            setattr(cf, 'organizerDisplayName', displayName)
        cf.check_initialized()
        return cf


    def _createConferenceObject(self, request):
        """Create or update Conference object, returning ConferenceForm/request."""
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['websafeConferenceKey']
        del data['organizerDisplayName']

        # add default values for those missing (both data model & outbound Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on start_date
        if data['startDate']:
            data['startDate'] = datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
            data['month'] = data['startDate'].month
        else:
            data['month'] = 0
        if data['endDate']:
            data['endDate'] = datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()

        # set seatsAvailable to be same as maxAttendees on creation
        if data["maxAttendees"] > 0:
            data["seatsAvailable"] = data["maxAttendees"]
        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        data['key'] = c_key
        data['organizerUserId'] = request.organizerUserId = user_id

        # create Conference, send email to organizer confirming
        # creation of Conference & return (modified) ConferenceForm
        Conference(**data).put()
        taskqueue.add(params={'email': user.email(),
            'conferenceInfo': repr(request)},
            url='/tasks/send_confirmation_email'
        )
        return request


    @ndb.transactional()
    def _updateConferenceObject(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}

        # update existing conference
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        # check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)

        # check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can update the conference.')

        # Not getting all the fields, so don't create a new object; just
        # copy relevant fields from ConferenceForm to Conference object
        for field in request.all_fields():
            data = getattr(request, field.name)
            # only copy fields where we get data
            if data not in (None, []):
                # special handling for dates (convert string to Date)
                if field.name in ('startDate', 'endDate'):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                    if field.name == 'startDate':
                        conf.month = data.month
                # write to Conference object
                setattr(conf, field.name, data)
        conf.put()
        prof = ndb.Key(Profile, user_id).get()
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))


    @endpoints.method(ConferenceForm, ConferenceForm, path='conference',
            http_method='POST', name='createConference')
    def createConference(self, request):
        """Create new conference."""
        return self._createConferenceObject(request)


    @endpoints.method(CONF_POST_REQUEST, ConferenceForm,
            path='conference/{websafeConferenceKey}',
            http_method='PUT', name='updateConference')
    def updateConference(self, request):
        """Update conference w/provided fields & return w/updated info."""
        return self._updateConferenceObject(request)


    @endpoints.method(CONF_GET_REQUEST, ConferenceForm,
            path='conference/{websafeConferenceKey}',
            http_method='GET', name='getConference')
    def getConference(self, request):
        """Return requested conference (by websafeConferenceKey)."""
        # get Conference object from request; bail if not found
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)
        prof = conf.key.parent().get()
        # return ConferenceForm
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
            path='getConferencesCreated',
            http_method='POST', name='getConferencesCreated')
    def getConferencesCreated(self, request):
        """Return conferences created by user."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # create ancestor query for all key matches for this user
        confs = Conference.query(ancestor=ndb.Key(Profile, user_id))
        prof = ndb.Key(Profile, user_id).get()
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, getattr(prof, 'displayName')) for conf in confs]
        )


    def _getQuery(self, request):
        """Return formatted query from the submitted filters."""
        q = Conference.query()
        inequality_filter, filters = self._formatFilters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Conference.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Conference.name)

        for filtr in filters:
            if filtr["field"] in ["month", "maxAttendees"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(filtr["field"], filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q


    def _formatFilters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name) for field in f.all_fields()}

            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                raise endpoints.BadRequestException("Filter contains invalid field or operator.")

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used in previous filters
                # disallow the filter if inequality was performed on a different field before
                # track the field on which the inequality operation is performed
                if inequality_field and inequality_field != filtr["field"]:
                    raise endpoints.BadRequestException("Inequality filter is allowed on only one field.")
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)


    @endpoints.method(ConferenceQueryForms, ConferenceForms,
            path='queryConferences',
            http_method='POST',
            name='queryConferences')
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


# - - - Session objects - - - - - - - - - - - - - - - - - - - -

    # Task 1
    def _copySessionToForm(self, sesh):
        """Copy relevant fields from Session to SessionForm."""
        sf = SessionForm()
        for field in sf.all_fields():
            if hasattr(sesh, field.name):
                # convert Date to date string; just copy others
                if field.name in ['startTime', 'date']:
                    setattr(sf, field.name, str(getattr(sesh, field.name)))
                else:
                    setattr(sf, field.name, getattr(sesh, field.name))
            elif field.name == "websafeSessionKey":
                setattr(sf, field.name, sesh.key.urlsafe())
        sf.check_initialized()
        return sf

    def _createSessionObject(self, request):
        """open only to the organizer of the conference"""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        if not request.sessionName:
            raise endpoints.BadRequestException("Session 'name' field required")

        # copy SessionForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['websafeSessionKey']
        # del data['websafeConferenceKey']

        # fetch and check conferencee
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)

        # ensure user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can add sessions.')

        # add default values for those missing (both data model & outbound Message)
        for df in SESHDEFAULTS:
            if data[df] in (None, []):
                data[df] = SESHDEFAULTS[df]
                setattr(request, df, SESHDEFAULTS[df])

        # convert dates from strings to Date objects; set month based on start_date
        if data['date']:
            data['date'] = datetime.strptime(data['date'][:10], "%Y-%m-%d").date()

        # convert time from strings to Time object (date-independent)
        if data['startTime']:
            data['startTime'] = datetime.strptime(data['startTime'][:5], "%H:%M").time()

        # converts type of session to string (TODO set as dropdown menu)
        if data['typeOfSession']:
            data['typeOfSession'] = str(data['typeOfSession'])


        # generate Session Key based on Conference key and organizer(?)
        # ID based on Profile key get Conference key from ID
        c_key = ndb.Key(Conference, conf.key.id())
        s_id = Session.allocate_ids(size=1, parent=c_key)[0]
        s_key = ndb.Key(Session, s_id, parent=c_key)
        data['key'] = s_key
        data['organizerUserId'] = request.organizerUserId = user_id
        del data['websafeConferenceKey']
        # del data['websafeSessionkey'] (only need to put if updating?)
        # del data['organizerUserId']

        Session(**data).put()

        speaker = Session.speaker

        logging.debug(speaker)
        print 'SPEAKERRRRRRRR: '
        print speaker
        print 'REQUEST.SPEAKERRR: '
        print request.speaker
        spkr = request.speaker
        # Task 4:
        # If number of sessions greater than one set featured speaker
        if len(data['speaker']) > 0:
            # for spkr in data['speaker']:
                taskqueue.add(
                    params={'speaker': spkr,
                            'websafeConferenceKey': request.websafeConferenceKey},
                    url='/tasks/set_featured_speaker')


        return request


    @endpoints.method(SessionForm, SessionForm,
                      path='conference/{websafeConferenceKey}/sessions/new',
                      http_method='POST', name='createSession')
    def createSession(self, request):
        """Open to the organizer of the conference"""
        return self._createSessionObject(request)


    @endpoints.method(CONF_GET_REQUEST, SessionForms, path='conference/{websafeConferenceKey}/sessions',
            http_method='GET', name='getConferenceSessions')
    def getConferenceSessions(self, request):
        """Return requested sessions (by websafeConferenceKey)."""

         # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}

        # get and check conf exists
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)


        # query for sessions with this conference as ancestor
        sessions = Session.query(ancestor=ndb.Key(Conference, conf.key.id()))
        # return set of SessionForm objects for conference
        return SessionForms(items=[self._copySessionToForm(session) for session in sessions])


    @endpoints.method(SESSION_GET_REQUEST, SessionForms,
                      path='sessions/{websafeConferenceKey}/{typeOfSession}',
                      http_method='GET', 
                      name='getConferenceSessionsByType')
    def getConferenceSessionsByType(self, request):
        """Return requested session (by session type)"""

         # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        typeOfSession = data['typeOfSession']

        # get and check conf exists
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % request.websafeConferenceKey)

        # query for sessions with this conference as ancestor and with equality filter on typeOfSession
        sessions = Session.query(Session.typeOfSession == typeOfSession, ancestor=ndb.Key(Conference, conf.key.id()))
        # return set of SessionForm objects for conference
        return SessionForms(items=[self._copySessionToForm(session) for session in sessions])

# - - - Speaker Functions - - - - - - - - - - - - - - - - - - -

    # Sets a memcache key to speaker
    @staticmethod
    def _setFeaturedSpeaker(featured_speaker, websafeConferenceKey):
        # Get Session Names associated with featured speaker
        # conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()

        sessions = Session.query(Session.speaker == featured_speaker, 
            ancestor=ndb.Key(urlsafe=websafeConferenceKey))

        #TODO NEED TO FIGURE OUT HOW TO ITERATE THROUGH SESSIONS AND PULL OUT SPEAKER
        print "Our Featured speaker is %s. For sessions: " % featured_speaker

        # Create message
        memcache_msg = "Our Featured speaker is %s. For sessions: " % featured_speaker

        for sess in sessions:
            memcache_msg += str(sess.sessionName) + ", "

        # Set memcache key
        memcache.set(MEMCACHE_FEATURED_SPEAKER, memcache_msg)


    @endpoints.method(SESSION_GET_REQUEST, SessionForms,
                      path='sessions/speaker',
                      http_method='GET', 
                      name='getConferenceSessionsBySpeaker')
    def getSessionsBySpeaker(self, request):
        """Return requested sessions (by speaker)"""
         # copy SessionForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        speaker = data['speaker']

        # query for sessions with this speaker as a match
        sessions = Session.query(Session.speaker == speaker)
        # return set of SessionForm objects for conference
        return SessionForms(items=[self._copySessionToForm(session) for session in sessions])



    @endpoints.method(message_types.VoidMessage, StringMessage,
            path='featuredspeaker/get',
            http_method='GET', name='getFeaturedSpeaker')
    def getFeaturedSpeaker(self, request):
        """Return Featured Speaker from memcache."""
        return StringMessage(data=memcache.get(MEMCACHE_FEATURED_SPEAKER) or "")



# - - - Wishlist Functions - - - - - - - - - - - - - - - - - - -

    @endpoints.method(WISH_POST_REQUEST, SessionForm,
                      path='conference/session/{websafeSessionKey}/wishlist/add', # necessarily want to add the websafeConferenceKey and websadesessionkey in the url here??
                      http_method='POST',
                      name='addSessionToWishlist')
    def addSessionToWishlist(self, request):
        """Adds a session to current user's wishlist"""
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get and check session
        session = ndb.Key(urlsafe=request.websafeSessionKey).get()
        if not session:
            raise endpoints.NotFoundException(
                'No session found with key: %s' % request.websafeSessionKey)

        # get profile
        prof = self._getProfileFromUser()

        # check if session in wishlist
        if session.key in prof.sessKeyWishlist:
            raise endpoints.BadRequestException(
                'Session already saved to wishlist: %s' % request.websafeSessionKey)

        # append to user profile's wishlist
        prof.sessKeyWishlist.append(session.key)
        prof.put()

        return self._copySessionToForm(session)

    @endpoints.method(message_types.VoidMessage, SessionForms,
            http_method='POST', name='getSessionsInWishlist')
    def getSessionsInWishlist(self, request):
        """Returns a user's session wishlist"""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get profile and wishlist
        prof = self._getProfileFromUser()
        s_keys = prof.sessKeyWishlist
        sessions = [s_key.get() for s_key in s_keys]

        # return list of sessions
        return SessionForms(
            items=[self._copySessionToForm(session) for session in sessions])


    @endpoints.method(WISH_POST_REQUEST, SessionForm,
                      path='conference/session/{websafeSessionKey}/wishlist/delete', # necessarily want to add the websafeConferenceKey and websadesessionkey in the url here??
                      http_method='POST',
                      name='deleteSessionInWishlist')
    def delete_session_from_wishlist(self, request):
        """Removes session from user's wishlist"""
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get and check session
        session = ndb.Key(urlsafe=request.websafeSessionKey).get()
        if not session:
            raise endpoints.NotFoundException(
                'No session found with key: %s' % request.websafeSessionKey)

        # get profile
        prof = self._getProfileFromUser()

        # check if session in wishlist
        if session.key not in prof.sessKeyWishlist:
            raise endpoints.BadRequestException(
                'Session not in wishlist: %s' % request.websafeSessionKey)

        # delete from user profile's wishlist 
        prof.sessKeyWishlist.remove(session.key)
        prof.put()

        return self._copySessionToForm(session)

# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'teeShirtSize':
                    setattr(pf, field.name, getattr(TeeShirtSize, getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()
        # create new Profile if not there
        if not profile:
            profile = Profile(
                key = p_key,
                displayName = user.nickname(),
                mainEmail= user.email(),
                teeShirtSize = str(TeeShirtSize.NOT_SPECIFIED),
            )
            profile.put()

        return profile      # return Profile

    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName', 'teeShirtSize'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
                        #if field == 'teeShirtSize':
                        #    setattr(prof, field, str(val).upper())
                        #else:
                        #    setattr(prof, field, val)
                        prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)

    @endpoints.method(message_types.VoidMessage, ProfileForm,
            path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()

    @endpoints.method(ProfileMiniForm, ProfileForm,
            path='profile', http_method='POST', name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)


# - - - Announcements - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def _cacheAnnouncement():
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        confs = Conference.query(ndb.AND(
            Conference.seatsAvailable <= 5,
            Conference.seatsAvailable > 0)
        ).fetch(projection=[Conference.name])

        if confs:
            # If there are almost sold out conferences,
            # format announcement and set it in memcache
            announcement = ANNOUNCEMENT_TPL % (
                ', '.join(conf.name for conf in confs))
            memcache.set(MEMCACHE_ANNOUNCEMENTS_KEY, announcement)
        else:
            # If there are no sold out conferences,
            # delete the memcache announcements entry
            announcement = ""
            memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)

        return announcement

    @endpoints.method(message_types.VoidMessage, StringMessage,
                      path='conference/announcement/get',
                      http_method='GET', name='getAnnouncement')
    def getAnnouncement(self, request):
        """Return Announcement from memcache."""
        return StringMessage(data=memcache.get(MEMCACHE_ANNOUNCEMENTS_KEY) or "")


# - - - Registration - - - - - - - - - - - - - - - - - - - -

    @ndb.transactional(xg=True)
    def _conferenceRegistration(self, request, reg=True):
        """Register or unregister user for selected conference."""
        retval = None
        prof = self._getProfileFromUser() # get user Profile

        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.websafeConferenceKey
        conf = ndb.Key(urlsafe=wsck).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % wsck)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsck in prof.conferenceKeysToAttend:
                raise ConflictException(
                    "You have already registered for this conference")

            # check if seats avail
            if conf.seatsAvailable <= 0:
                raise ConflictException(
                    "There are no seats available.")

            # register user, take away one seat
            prof.conferenceKeysToAttend.append(wsck)
            conf.seatsAvailable -= 1
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsck in prof.conferenceKeysToAttend:

                # unregister user, add back one seat
                prof.conferenceKeysToAttend.remove(wsck)
                conf.seatsAvailable += 1
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        conf.put()
        return BooleanMessage(data=retval)


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
            path='conferences/attending',
            http_method='GET', name='getConferencesToAttend')
    def getConferencesToAttend(self, request):
        """Get list of conferences that user has registered for."""
        prof = self._getProfileFromUser() # get user Profile
        conf_keys = [ndb.Key(urlsafe=wsck) for wsck in prof.conferenceKeysToAttend]
        conferences = ndb.get_multi(conf_keys)

        # get organizers
        organisers = [ndb.Key(Profile, conf.organizerUserId) for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return set of ConferenceForm objects per Conference
        return ConferenceForms(items=[self._copyConferenceToForm(conf, names[conf.organizerUserId])\
         for conf in conferences]
        )


    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
            path='conference/{websafeConferenceKey}',
            http_method='POST', name='registerForConference')
    def registerForConference(self, request):
        """Register user for selected conference."""
        return self._conferenceRegistration(request)


    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
            path='conference/{websafeConferenceKey}',
            http_method='DELETE', name='unregisterFromConference')
    def unregisterFromConference(self, request):
        """Unregister user for selected conference."""
        return self._conferenceRegistration(request, reg=False)


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
            path='filterPlayground',
            http_method='GET', name='filterPlayground')
    def filterPlayground(self, request):
        """Filter Playground"""
        q = Conference.query()
        # field = "city"
        # operator = "="
        # value = "London"
        # f = ndb.query.FilterNode(field, operator, value)
        # q = q.filter(f)
        q = q.filter(Conference.city=="London")
        q = q.filter(Conference.topics=="Medical Innovations")
        q = q.filter(Conference.month==6)

        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, "") for conf in q]
        )


# - - - Social Feed Query Functions - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(SocialForm, SocialForms,
            path='conference/{websafeConferenceKey}/socialfeed',
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

        # pull up other users of that conference (query by kind, filter by property)
        profiles = Profile.all()

        logging.debug(profiles)

        # iterate through conferencestoattend array 
        attendant_keys = []
        for prof in profiles:
            for c in prof.conferenceKeysToAttend:
                if c == conf:
                    attendant_keys.append(prof.key)

        logging.debug(attendant_keys)
        
        # get final list of attendants
        attendants = ndb.get_multi(attendant_keys)

        # # set equality filter and where conf exists in user's conferenceKeysToAttend
        # profiles.filter(Profile.conferenceKeysToAttend == conf)
        logging.debug('*******MARKER FOR PROFILE LIST QUERY')
        logging.debug(attendants)

        # return other users of that conference
        # return SocialForms(
        # items=[self._copyProfileToForm(prof) for prof in profiles])
# ORRRRRRR

        return SocialForms(
        socialList=[self._copyProfileToForm(getattr(prof, 'displayName')) for prof in attendants])

# - - - Other Query Functions - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(message_types.VoidMessage, SessionForms,
                      path='sessions/past',
                      http_method='GET',
                      name='getPastSessions')
    def getPastSessions(self, request):
        """Return sessions that have occurred in the past."""
        # copy SessionForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        sessions = Session.query(Session.date < datetime.now()).fetch()
        # return set of SessionForm objects for conference
        return SessionForms(items=[self._copySessionToForm(session) for session in sessions])


    @endpoints.method(message_types.VoidMessage, SessionForms,
                      path='sessions/getSessionsByTypeTime',
                      http_method='GET', name='getSessionsByTypeTime')
    def getSessionsByTypeTime(self, request):
        """Returns all non workshop sessions held before 7 pm. """

        sessions = Session.query(ndb.AND(
                   Session.startTime != None,
                   Session.startTime <= timed(hour=19)))

        filtered_sessions = []
        for session in sessions:
            if 'workshop' == session.typeOfSession:
                continue
            else:
                filtered_sessions.append(session)

        return SessionForms(
            items=[self._copySessionToForm(session) for session in filtered_sessions]
        )

api = endpoints.api_server([ConferenceApi]) # register API
