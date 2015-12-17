import sys 
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship # creates foreign key relationships
from sqlalchemy import create_engine 
Base = declarative_base() # lets sqlalchemy know that our classes are  special sqlalchemy classes that correspond to tables in DB


# classes
class user(Base):

	__tablename__ = 'user'

	userID = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	email = Column(String(80), nullable = False)
	picture = Column(String(250))

class domain(Base) :
	
	__tablename__ = 'domain'

	domID = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	userID = Column(Integer, ForeignKey('user.userID'))
	pullUser = relationship(user)
	# starcounter = relationship(event) TODO
	
	@property
	def serialize(self):
		"""Return object data in easily serializable format"""
		return {
				'name': self.name,
				'id': self.domID,
		}
	
class event(Base):

	__tablename__ = 'events'

	eventID = Column(Integer, primary_key = True)
	# image = BLOB()
	name = Column(String(80), nullable = False)
	category = Column(String(250))
	description = Column(String(250))
	thumbnail_url = Column(String(255))
	stars = Column(Integer, nullable = False)
	domID = Column(Integer, ForeignKey('domain.domID'))
	dom = relationship(domain)
	userID = Column(Integer, ForeignKey('user.userID'))
	pullUser = relationship(user)

	@property
	def serialize(self):
		"""Return object data in easily serializable format"""
		return {
			'name': self.name,
			'description': self.description,
			'id': self.eventID,
			'stars': self.stars,
			'category': self.category,
		}
	


#### configuration to insert at end of file ####

engine = create_engine('sqlite:///goldstarswithusers.db')

Base.metadata.create_all(engine) # goes into DB and adds classes as new tables to DB