# final app model additions
# The Session class is created as a child of the conference.
Sessions can have speakers, start time, duration, type of session (workshop, lecture etc…), 
location. You will need to define the Session class and the SessionForm class, as well as appropriate Endpoints.
You are free to choose how you want to define speakers, eg just as a string or as a full fledged entity.


class Session(ndb.Model):
    """Session -- Session object"""
    sessionName     = ndb.StringField(required=True)
    highlights    	= ndb.StringField(repeated=True)
    speaker			= ndb.StringField(required=True)
    duration        = ndb.IntegerField()
    typeOfSession   = ndb.StringField() # use enum?
    date       		= ndb.IntegerField()
    startTime       = ndb.TimeProperty() # in 24 hr notation so it can be ordered

class SessionForm(messages.Message):
    """SessionForm -- Session outbound form message"""
    sessionName          = messages.StringField(1)
    highlights    	     = messages.StringField(2)
    speaker			     = messages.StringField(3)
    duration             = messages.StringField(4)
    typeOfSession        = messages.StringField(5, repeated=True) # use enum?
    date       		     = messages.StringField(6) # DateTimeField()
    startTime            = messages.StringField(7) # DateTimeField()
    websafeSessionKey = messages.StringField(8)
    organizerDisplayName = messages.StringField(9)


class SessionQueryForm(messages.Message):
    """SessionQueryForm -- Session query inbound form message"""
    field = messages.StringField(1)
    operator = messages.StringField(2)
    value = messages.StringField(3)

class SessionQueryForms(messages.Message):
    """ConferenceQueryForms -- multiple SessionQueryForm inbound form message"""
    filters = messages.MessageField(SessionQueryForm, 1, repeated=True)




class Wishlist(ndb.Model):
    userID = ndb.StringProperty(required=True)
    c_key  = ndb.KeyProperty(kind='Conference', required=True)
    s_keys = ndb.KeyProperty(kind='Session', repeated=True)

class WishlistForm(messages.Message):
    userID = messages.StringField(1)
    websafeSessionKey = messages.StringField(2)
    websafeKey = messages.StringField(3)

