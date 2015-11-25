# final app model additions


# Ideally, create the session as a child of the conference.
Sessions can have speakers, start time, duration, type of session (workshop, lecture etc…), location. You will need to define the Session class and the SessionForm class, as well as appropriate Endpoints.
You are free to choose how you want to define speakers, eg just as a string or as a full fledged entity.


class Session(Conference or ndb.Model):
    """Session -- Session object"""
    sessionName     = ndb.StringField(required=True)
    highlights    	= ndb.StringField(repeated=True)
    speaker			= ndb.StringField()
    duration        = ndb.IntegerField()
    typeOfSession   = ndb.StringField() # use enum?
    date       		= ndb.IntegerField()
    startTime       = ndb.IntegerField() # in 24 hr notation so it can be ordered

class SessionForm(messages.Message):
    """SessionForm -- Session outbound form message"""
    sessionName     = messages.StringField(1)
    highlights    	= messages.StringField(2)
    speaker			= messages.StringField(3)
    duration        = messages.StringField(4, repeated=True)
    typeOfSession   = messages.StringField(5) # use enum?
    date       		= messages.IntegerField(6)
    startTime       = messages.IntegerField(7) # in 24 hr notation so it can be ordered
