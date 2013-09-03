#! /usr/bin/python2
## Copyright (c) 2013, Satvik Chauhan
##
## All rights reserved.
##
## This software is distributed under the terms and conditions of the
## BSD3 license. See the accompanying file LICENSE for exact terms and
## condition.


import urllib, urllib2, cookielib, re, pickle, itertools
from lxml import etree
import way2

nfile = "Notices.p"
numberfile = "numbers.txt"
userfile = "pasuser.txt"

# Read the numbers to be notified
with open(numberfile,"r") as fp:
		numbers = fp.read().splitlines()

# Read PAS account details
with open(userfile,"r") as fp:
		data = fp.read().splitlines()
		username = data[0]
		password = data[1]

# Construct a opener with cookie support
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
resp = opener.open('http://placement.iitk.ac.in/pas/login')
s = resp.read()

# Submit the PAS login form
data = dict()
data['authenticity_token'] = re.findall('<input name="authenticity_token" type="hidden" value="([^"]+)"', s)[0]
data['userlogin_session[login]'] = username
data['userlogin_session[password]'] = password


html = etree.HTML(opener.open('http://placement.iitk.ac.in/pas/userlogin_sessions', urllib.urlencode(data)).read())

# Get All the notifications on the page
xpath = '//table/tr'
filtered_html = html.xpath(xpath)
notices = [0] * len(filtered_html)
for i,node in enumerate(filtered_html):
		notice = dict()
		for j,n in enumerate(node.xpath("./td")):
				notice[j] = n.text
		notices[i] = notice

# Load notifications on last check
try:
		lastnotices = pickle.load(open(nfile,"rb"))
except:
		lastnotices = notices

# Find new notifications and send them
if lastnotices != []:
		newnotices = list(itertools.takewhile(lambda x: x != lastnotices[0], notices))
		if newnotices != []:
				for nt in newnotices:
						for n in numbers:
								i = 10
								while i > 0:
										try:
												handler = way2.smsHandler(way2.username,way2.password)
												handler.do(n,'-'.join(nt.values()))
												i = 0
										except:
												i = i - 1

# Save the latest notifications
with open(nfile,"wb") as fp:
		pickle.dump(notices,fp)
