from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# common gateway interface for do_POST()
import cgi

# import CRUD operations and modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, domain, event

# create session and connect to DB
engine = create_engine('sqlite:///healthevents.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	# get information already on the server, simply visiting the url
	def do_GET(self):
		
		if self.path.endswith("/domains/new"):
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			output = ""
			output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
			output += "<h1>List a new domain!</h1>"
			output += "<form method='POST' enctype='multipart/form-data' action='/domains/new'>"
			output += "<input name='domainname'type='text' placeholder = 'New domain name'>"
			output += "<input type='submit' value='Create'>"                
			output += "</form></html></body>"
			self.wfile.write(output)
			print output
			return

		if self.path.endswith("/domains"):

			domains = session.query(domain).all()
			# send indication of successful post
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			output = ""
			output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
			output += "<a href='/domains/new'>List a new domain here</a>"
			output += "<h1>domains:</h1>"
			for i in domains:
				output += '<h2>' 
				output += i.name 
				output += '</h2>'
				output += '</br>'
				output += '<a href="domains/%s/edit">Edit</a></br>' % i.domID
				output += '<a href="domains/%s/delete">Delete</a></br>' % i.domID
				output += '<a href="domains/%s/events">events</a></br>' % i.domID
				output += '</br>'

			output += "</html></body>"          
			self.wfile.write(output)
			print output
			return

		if self.path.endswith("/edit"):
			# pulls id from url
			domIDpath = self.path.split("/")[2]
			# grabs domain entry from DB equal to the ID in the URL
			nameToEdit = session.query(domain).filter_by(domID = domIDpath).one()    
			# if query found, generate response and begin to render page
			if nameToEdit != [] :
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
				output += "<h1>Edit a domain name!</h1>"       
				output += "<form method='POST' enctype='multipart/form-data' action='/domains/%s/edit'>" % domIDpath
				output += "<input name='domainname'type='text' placeholder = '%s'>" % nameToEdit.name
				output += "<input type='submit' value='Rename'>"                
				output += "</form></html></body>"
				self.wfile.write(output)
				print output
				return  

		if self.path.endswith("/eventedit"):
			# pulls id from url
			domIDpath = self.path.split("/")[2]
			eventIDpath = self.path.split("/")[2] # CHANGE
			# grabs domain entry from DB equal to the ID in the URL
			eventToEdit = session.query(event).filter_by(domID = domIDpath).one()    
			# if query found, generate response and begin to render page
			if eventToEdit != [] :
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
				output += "<h1>Edit an event name!</h1>"       
				output += "<form method='POST' enctype='multipart/form-data' action='/domains/%s/edit'>" % domIDpath
				output += "<input name='eventname'type='text' placeholder = '%s'>" % eventToEdit.name
				output += "<input type='submit' value='Rename'>"                
				output += "</form></html></body>"
				self.wfile.write(output)
				print output
				return 


		if self.path.endswith("/events"):
			domIDpath = self.path.split("/")[2]
			## how do i extract the domain name from the domID?
			eventsRead = session.query(event).filter_by(domID = domIDpath).all()
			domNamePath = session.query(domain).filter_by(domID = domIDpath).all()

			# send indication of successful post
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			output = ""
			output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
			output += "<a href='/domains/%s/events/new'>List a new event here</a>" % domIDpath
			output += "</br>"
			output += "<a href='/domains'>Go back to domain listings</a>"
			for dom in domNamePath:          
				output += "<h1>events in %s:</h1>" % dom.name
				for i in eventsRead:
					output += "<h2>" 
					output += i.name 
					output += "</h2>"
					output += "</br>"
					output += "<a href='domains/%s/events/%s/eventedit'>Edit</a></br>" % (domIDpath, i.eventID)
					output += "<a href='/events/%s/eventdelete'>Delete</a></br>" % (i.eventID)
					output += "</br>"
			output += "</html></body>"          
			self.wfile.write(output)
			print output
			return

				 # to add a new event, assigned to a domain			
		if self.path.endswith("/events/new"):

			domIDpath = self.path.split("/")[2]
			# grabs domain entry from DB equal to the ID in the URL
			eventdomain = session.query(domain).filter_by(domID = domIDpath).one()   
			# if query found, generate response and begin to render page
			if eventdomain != [] :
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
				output += "<h1>Add an event to the domain's list!</h1>"
				output += "<form method='POST' enctype='multipart/form-data' action='/domains/%s/events/new'>" % domIDpath
				output += "<input name='newevent'type='text' placeholder = 'What is the new event name?'>"
				output += "<input type='submit' value='Create'>"                
				output += "</form></html></body>"
				self.wfile.write(output)
				print output
				return  


		if self.path.endswith("/delete"):
			domIDPath = self.path.split("/")[2]
			domToDelete = session.query(domain).filter_by(domID=domIDPath).one()
			
			if domToDelete:
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body><STYLE TYPE='text/css'> <!-- BODY { color:#F0F8FF; background-color:#56C9CC; font-family:sans-serif; } A:link{color:white} A:visited{color:yellow} --> </STYLE>"
				output += "<h2>"
				output += "Are you sure you want to delete %s?" % domToDelete.name
				output += "</h2>"
				output += "</br>"
				output += "<form method='POST' enctype = 'multipart/form-data' action = '/domains/%s/delete'>" % domIDPath
				output += "<input type = 'submit' value = 'Delete'>"
				output += "</form>"
				output += "</body></html>"
				self.wfile.write(output)  

		# if self.path.endswith("/eventdelete"):
		# 	domIDPath = self.path.split("/")[2]
		# 	eventIDPath = self.path.split("/")[6]
		# 	eventToDelete = session.query(event).filter_by(domID=domIDPath, eventID=eventIDPath).one()
		# 	if eventToDelete:
		# 		self.send_response(200)
		# 		self.send_header('Content-type', 'text/html')
		# 		self.end_headers()
		# 		output = ""
		# 		output += "<html><body>"
		# 		output += "<h1>Are you sure you want to delete %s?" % eventToDelete.name
		# 		output += "<form method='POST' enctype = 'multipart/form-data' action = '/domains/%s/eventdelete'>" % eventIDPath
		# 		output += "<input type = 'submit' value = 'Delete'>"
		# 		output += "</form>"
		# 		output += "</body></html>"
		# 		self.wfile.write(output)  

				# post adds new information (also overrides the method in the 
				# BaseHTTPhandler superclass just like do_GET)
				#cannot be executed by simply typing URL into browser and clicking 'enter'
				#do post is going to look for the /domains/new path 
				#passed along from my form, in order to know what action to perform

	def do_POST(self):
		try:
			if self.path.endswith("/domains/new"):
				# extract information from form
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('domainname')
				
					# incorporate extracted data into declaration of new restaurant class
					# create a new domain class
					newdomain = domain(name = messagecontent[0])
					session.add(newdomain)
					session.commit()
					
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					# instead of printing results to current webpage,               
					# redirect that takes user back to homepage
					self.send_header('Location', '/domains')
					self.end_headers()
			
			if self.path.endswith("/edit"):
				# extract information from form
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('domainname')
					domIDpath = self.path.split("/")[2]

					nameToEdit = session.query(domain).filter_by(domID = domIDpath).one()

					if nameToEdit != []:
						nameToEdit.name = messagecontent[0]
						session.add(nameToEdit)
						session.commit()
					
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						# instead of printing results to current webpage,               
						# redirect that takes user back to homepage
						self.send_header('Location', '/domains')
						self.end_headers()
			
			if self.path.endswith("/eventedit"):
				# extract information from form

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				eventIDpath = self.path.split("/")[6]
				nameToEdit = session.query(event).filter_by(eventID = eventIDpath).one()

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('eventname')

					if nameToEdit != []:
						nameToEdit.name = messagecontent[0]
						session.add(nameToEdit)
						session.commit()
					
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						# instead of printing results to current webpage,               
						# redirect that takes user back to homepage
						self.send_header('Location', '/domains')
						self.end_headers()

			if self.path.endswith("/events/new"):
				# extract information from form
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				domIDPath = self.path.split("/")[2]
				domNamePath = session.query(domain).filter_by(domID = domIDpath).one()

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newevent')
				
					# incorporate extracted data into declaration of new domain class
					# create a new domain class
					newevent = event(name = messagecontent[0]) # dom=domain(name="%s")) % domNamePath [question how do i get event to insert being assigned to specific domain that is pulled from url path]
					session.add(newevent)
					session.commit()
					
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					# instead of printing results to current webpage,               
					# redirect that takes user back to homepage
					self.send_header('Location', '/domains')
					self.end_headers()

			if self.path.endswith("/delete"):
				domIDPath = self.path.split("/")[2]
				domToDelete = session.query(domain).filter_by(domID=domIDPath).one()
				print "this is the value of domToDelete" , domToDelete
				if domToDelete: 
					print "this is when domToDelete is deleted"
					session.delete(domToDelete)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/domains')
					self.end_headers()
				else:
					self.send_response(404)


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

