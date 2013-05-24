# -*- coding: ISO-8859-1 -*-
from time import gmtime, strftime
import urllib, urllib2, cookielib
import os, sys
from HTMLParser import HTMLParser

#Config
USER = ''
PASSWORD = ''

class MyParser(HTMLParser):
	startPoint = 0    #When should we start parsing
	newCourse = 0     #Have we found a new course?
	tdCount = 99      #How many TD's have we seen?
	results = []      #The list of results

	def handle_starttag(self, tag, attrs):
		#If we've passed the startingpoint, we start parsing
		if self.startPoint == 1:
			if tag == "tr":
			#We've found a new course
				self.newCourse = 1
				self.tdCount = 0
			if tag == "td":
				self.tdCount = self.tdCount + 1

	def handle_data(self, data):
		global results
		#We've found the table, and starts our search
		if data == "ECTS":
			self.startPoint = 1

		#1 TD's from the tr lays the coursename
		#4 TD's from the tr lays the grade
		if self.tdCount == 1:
			self.tdCount = self.tdCount + 1
			self.results.append(data.strip())

		if self.tdCount == 4:
			self.tdCount = self.tdCount + 1
			self.results.append(data)

class Fetcher():

	html = ""
	username = ""
	password = ""

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def fetch(self):
		#We start by getting initial cookie, from stads
		cj = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		opener.open('https://stadssb.au.dk/SBSTADSC1P/sb/index.jsp')

		print "Brugernavn: ", self.username
		print "Kode: ", self.password

		#And then we craft our post request to get our login token
		login_data = urllib.urlencode({'lang' : 'null', 'submit_action' : 'login', 'brugernavn' : self.username, 'adgangskode' : self.password})
		opener.open('https://stadssb.au.dk/SBSTADSC1P/sb/index.jsp', login_data)
		resp = opener.open('https://stadssb.au.dk/SBSTADSC1P/sb/resultater/studresultater.jsp')
		self.html = resp.read()

if __name__ == '__main__':

    if (USER == '') or (PASSWORD == ''):
        sys.exit('Error: Empty username or password')

	results = []
	scriptDir = os.path.dirname(os.path.abspath(__file__))

	### Fetch the html
	fetcher = Fetcher(USER, PASSWORD)
	fetcher.fetch()
	html = fetcher.html

	### Parse the html
	parser = MyParser()
	parser.feed(html)
	results = parser.results

	### See if theres any change
	## Previous number of courses
	f = open(scriptDir + '/gradedCourses.log', 'a+')
	prevCourses = int('0' + f.read())
	f.close()

	## Current number of courses
	currCourses = len(results)/2

	newGrades = currCourses - prevCourses

	if (newGrades > 0) and (currCourses != 0):
		message  = "Der er kommet nye karakterer. "
		message += "Du har fået "

		for i in range(0, newGrades):
			message += results[1 + i*2]
			message += " i "
			message += results[0 + i*2]
			message += ", "

		message = message[:-2]
		message += "."

		print message

		f = open (scriptDir + '/gradedCourses.log', 'w')
		f.write(str(currCourses))
		f.close()
