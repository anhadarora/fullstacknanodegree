from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# common gateway interface for do_POST()
import cgi

# import CRUD operations and modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, company, item

# create session and connect to DB
engine = create_engine('sqlite:///healthitems.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	# get information already on the server, simply visiting the url
	def do_GET(self):
		
		if self.path.endswith("/companies/new"):
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			output = ""
			output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
			output += "<h1>List a new company!</h1>"
			output += "<form method='POST' enctype='multipart/form-data' action='/companies/new'>"
			output += "<input name='companyname'type='text' placeholder = 'New company name'>"
			output += "<input type='submit' value='Create'>"				
		 	output += "</form></html></body>"
			self.wfile.write(output)
			print output
			return

		if self.path.endswith("/companies"):

			companies = session.query(company).all()
			# send indication of successful post
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			output = ""
			output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
			output += "<a href='/companies/new'>List a new company here</a>"
			output += "<h1>Companies:</h1>"
			for i in companies:
				output += '<h2>' 
				output += i.name 
				output += '</h2>'
				output += '</br>'
				output += '<a href="companies/%s/edit">Edit</a></br>' % i.compID
				output += '<a href="companies/%s/delete">Delete</a></br>' % i.compID
				output += '<a href="companies/%s/items">Items</a></br>' % i.compID
				output += '</br>'

			output += "</html></body>"			
			self.wfile.write(output)
			print output
			return

		if self.path.endswith("/edit"):
			# pulls id from url
			compIDpath = self.path.split("/")[2]
			# grabs company entry from DB equal to the ID in the URL
			nameToEdit = session.query(company).filter_by(compID = compIDpath).one() 	
			# if query found, generate response and begin to render page
			if nameToEdit != [] :
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
				output += "<h1>Edit a company name!</h1>"		
				output += "<form method='POST' enctype='multipart/form-data' action='/companies/%s/edit'>" % compIDpath
				output += "<input name='companyname'type='text' placeholder = '%s'>" % nameToEdit.name
				output += "<input type='submit' value='Rename'>"				
			 	output += "</form></html></body>"
				self.wfile.write(output)
				print output
				return	

# to add a new item, assigned to a company
		if self.path.endswith("/itemsnew"):

			compIDpath = self.path.split("/")[2]
			# grabs company entry from DB equal to the ID in the URL
			itemCompany = session.query(company).filter_by(compID = compIDpath).one() 	
			# if query found, generate response and begin to render page
			if itemCompany != [] :
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
				output += "<h1>Add an item to the company's list!</h1>"
				output += "<form method='POST' enctype='multipart/form-data' action='/companies/%s/itemsnew'>" % compIDpath
				output += "<input name='itemname'type='text' placeholder = 'What is the new item name?'>"
				output += "<input type='submit' value='Create'>"				
			 	output += "</form></html></body>"
				self.wfile.write(output)
				print output
				return	



		if self.path.endswith("/items"):
			compIDpath = self.path.split("/")[2]
			## how do i extract the company name from the compID?
			itemsRead = session.query(item).filter_by(compID = compIDpath)
			compNamepath = session.query(company.name).filter_by(compID = compIDpath)

			# send indication of successful post
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			output = ""
			output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
			output += "<a href='/companies/%s/itemsnew'>List a new item here</a>" % compIDpath
			output += "<a href='/companies'>Go back to company listings</a>"
			output += "<h1>Items in %s:</h1>" % compNamepath
			for i in itemsRead:
				output += '<h2>' 
				output += i.name 
				output += '</h2>'
				output += '</br>'
				output += '<a href="companies/%s/edit">Edit</a></br>' % i.itemID
				output += '<a href="companies/%s/delete">Delete</a></br>' % i.itemID
				output += '</br>'
			output += "</html></body>"			
			self.wfile.write(output)
			print output
			return
	
	# post adds new information (also overrides the method in the 
	# BaseHTTPhandler superclass just like do_GET)
#cannot be executed by simply typing URL into browser and clicking 'enter'
#do post is going to look for the /companies/new path 
#passed along from my form, in order to know what action to perform

	def do_POST(self):
		try:
			if self.path.endswith("/companies/new"):
				# extract information from form
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('companyname')
				
					# incorporate extracted data into declaration of new restaurant class
					# create a new company class
					newcompany = company(name = messagecontent[0])
					session.add(newcompany)
					session.commit()
					
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					# instead of printing results to current webpage,				
					# redirect that takes user back to homepage
					self.send_header('Location', '/companies')
					self.end_headers()
			
			if self.path.endswith("/edit"):
				# extract information from form
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('companyname')
					compIDpath = self.path.split("/")[2]

					nameToEdit = session.query(company).filter_by(compID = compIDpath).one()
					if nameToEdit != []:
						nameToEdit.name = messagecontent[0]
						session.add(nameToEdit)
						session.commit()
					
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						# instead of printing results to current webpage,				
						# redirect that takes user back to homepage
						self.send_header('Location', '/companies')
						self.end_headers()		
		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__ == '__main__':
	main()
