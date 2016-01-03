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

class company(Base) :
	
	__tablename__ = 'company'

	compID = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	userID = Column(Integer, ForeignKey('user.userID'))
	pullUser = relationship(user)
	
	@property
	def serialize(self):
		"""Return object data in easily serializable format"""
		return {
				'name': self.name,
				'id': self.compID,
		}
	
class item(Base):

	__tablename__ = 'items'

	itemID = Column(Integer, primary_key = True)
	# image = BLOB()
	name = Column(String(80), nullable = False)
	category = Column(String(250))
	description = Column(String(250))
	price = Column(String(8))
	compID = Column(Integer, ForeignKey('company.compID'))
	comp = relationship(company)
	userID = Column(Integer, ForeignKey('user.userID'))
	pullUser = relationship(user)

	@property
	def serialize(self):
		"""Return object data in easily serializable format"""
		return {
			'name': self.name,
			'description': self.description,
			'id': self.itemID,
			'price': self.price,
			'category': self.category,
		}
	



#### configuration to insert at end of file ####

engine = create_engine('sqlite:///healthitemswithusers.db')

Base.metadata.create_all(engine) # goes into DB and adds classes as new tables to DB