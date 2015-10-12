# configuration doesn't change much

import sys 
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship # creates foreign key relationships
from sqlalchemy import create_engine 
Base = declarative_base() # lets sqlalchemy know that our classes are 
						  # special sqlalchemy classes that correspond to tables in DB

# classes

class company(Base) :
	
	__tablename__ = 'company'

	compID = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)

class item(Base):

	__tablename__ = 'items'

	itemID = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	category = Column(String(250))
	description = Column(String(250))
	price = Column(String(8))
	compID = Column(Integer, ForeignKey('company.compID'))
	company = relationship(company)


#### configuration to insert at end of file ####

engine = create_engine('sqlite:///healthitems.db')

Base.metadata.create_all(engine) # goes into DB and adds classes as new tables to DB
