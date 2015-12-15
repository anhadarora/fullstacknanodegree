from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, domain, event

engine = create_engine('sqlite:///healthevents.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()


Jawbone = domain(domID = "1", name = "Jawbone")
JawboneUP3 = event(eventID=1, 
                  name="Jawbone UP3", 
                  description="The latest UP!", 
                  category="tracker", 
                  stars="$174.99", 
                  domain=domain(name="Jawbone"))

session.add(Jawbone)
session.add(JawboneUP3)

session.commit()

session.query(domain).all()
session.query(event).all()

# using py 'for' loop to read and query the data
# variable that corresponds to single row in DB
# these references allow to extract column entries as method names
firstResult = session.query(domain).first()
firstResult.name

events = session.query(events).all()
for event in events:
	print event.name


jawboneList = session.query(domain).filter_by(name= 'Jawbone') 
	for i in jawboneList:  
	   print i.id     
	   print i.stars     
	   print i.domain.name     
	   print "\n"