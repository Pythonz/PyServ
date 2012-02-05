#!/usr/bin/env python

import sys
import socket
import os
import thread
import ConfigParser
import time
import hashlib
import smtplib
import _mysql
import git

repo = git.Repo(".")
i = 1
while len(repo.commits("master", max_count=i)) == i:
	i += 1
__version__ = (len(repo.commits("master", max_count=i)))
_started = time.time()
config = ConfigParser.RawConfigParser()
config.read("pyserv.conf")

def debug(text):
	if config.get("OTHER", "debug") == "1":
		print(str(text))

class Services:
	def __init__(self):
		self.mysql_host = config.get("MYSQL", "host")
		self.mysql_port = config.getint("MYSQL", "port")
		self.mysql_name = config.get("MYSQL", "name")
		self.mysql_user = config.get("MYSQL", "user")
		self.mysql_passwd = config.get("MYSQL", "passwd")
		self.server_name = config.get("SERVER", "name")
		self.server_address = config.get("SERVER", "address")
		self.server_port = config.get("SERVER", "port")
		self.server_id = config.get("SERVER", "id")
		self.server_password = config.get("SERVER", "password")
		self.services_name = config.get("SERVICES", "name")
		self.services_id = config.get("SERVICES", "id")
		self.services_description = config.get("SERVICES", "description")
		self.debug = config.get("OTHER", "debug")
		self.email = config.get("OTHER", "email")
		self.regmail = config.get("OTHER", "regmail")
		self.bot = "%sAAAAAA" % self.services_id
		self.obot = "%sAAAAAB" % self.services_id
		self.db = _mysql.connect(host=self.mysql_host, port=self.mysql_port, db=self.mysql_name, user=self.mysql_user, passwd=self.mysql_passwd)

	def run(self):
		try:
			self.query("delete from temp_nick")
			self.query("delete from opers")
			self.query("delete from online")
			self.con = socket.socket()
			self.con.connect((self.server_address, int(self.server_port)))
			self.send("SERVER %s %s 0 %s :%s" % (self.services_name, self.server_password, self.services_id, self.services_description))
			self.send(":%s BURST" % self.services_id)
			self.send(":%s ENDBURST" % self.services_id)
			
			while 1:
				recv = self.con.recv(5120)
				if not recv:
					self.reconnect()
					return 0
				for data in recv.rstrip().split("\n"):
					debug("<< %s" % data)
					if data.rstrip() != "":
						if data.split()[1] == "PING":
							self.send(":%s PONG %s %s" % (self.services_id, self.services_id, data.split()[2]))
							self.send(":%s PING %s %s" % (self.services_id, self.services_id, data.split()[2]))
						if data.split()[1] == "ENDBURST":
							self.send(":%s UID %s %s Q %s %s TheQBot 0.0.0.0 %s +I :The Q Bot" % (self.services_id, self.bot, time.time(), self.services_name, self.services_name, time.time()))
							self.send(":%s OPERTYPE Service" % self.bot)
							self.join("#opers")
							self.join("#services")
							self.meta(self.bot, "accountname", "Q")
							self.send(":%s UID %s %s O %s %s TheOBot 0.0.0.0 %s +I :The O Bot" % (self.services_id, self.obot, time.time(), self.services_name, self.services_name, time.time()))
							self.send(":%s OPERTYPE Service" % self.obot)
							self.ojoin("#opers")
							self.ojoin("#services")
							self.meta(self.obot, "accountname", "O")
							self.omsg("$*", "Services are now back online. Have a nice day :)")
							self.version(self.obot, "$*")
							for channel in self.query("select name from channelinfo"):
								self.join(str(channel[0]))
						if data.split()[1] == "PRIVMSG":
							if data.split()[2] == self.bot:
								self.message(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
							if data.split()[2] == self.obot:
								self.omessage(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
						if data.split()[1] == "NICK":
							self.query("update online set nick = '%s' where uid = '%s'" % (data.split()[2], str(data.split()[0])[1:]))
						if data.split()[1] == "QUIT":
							self.query("delete from temp_nick where nick = '%s'" % str(data.split()[0])[1:])
							self.query("delete from online where uid = '%s'" % str(data.split()[0])[1:])
						if data.split()[1] == "TOPIC":
							if len(data.split()) > 1:
								if self.chanflag("t", data.split()[2]):
									for channel in self.query("select topic from channel where name = '{0}'".format(data.split()[2])):
										self.send(":{0} TOPIC {1} :{2}".format(self.bot, data.split()[2], channel[0]))
						if data.split()[1] == "FMODE":
							if self.chanflag("m", data.split()[2]):
								if data.split()[2].startswith("#"):
									for channel in self.query("select name,modes from channelinfo where name = '{0}'".format(data.split()[2])):
										self.mode(channel[0], channel[1])
							if len(data.split()) > 5:
								if self.chanflag("p", data.split()[2]):
									for user in data.split()[5:]:
										for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (data.split()[2], self.auth(user))):
											if str(flag[0]) == "n":
												self.mode(data.split()[2], "+q %s" % user)
											elif str(flag[0]) == "Y":
												pass
											else:
												self.mode(data.split()[2], "+%s %s" % (str(flag[0]), user))
						if data.split()[1] == "FJOIN":
							fjoin_chan = data.split()[2]
							fjoin_nick = data.split()[5][1:]
							if fjoin_nick.startswith(","):
								fjoin_nick = fjoin_nick[1:]
							fjoin_user = self.auth(fjoin_nick)
							hasflag = False
							for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (fjoin_chan, fjoin_user)):
								if str(flag[0]) == "n":
									self.mode(fjoin_chan, "+q %s" % fjoin_nick)
									hasflag = True
								elif str(flag[0]) == "Y":
									pass
								else:
									self.mode(fjoin_chan, "+%s %s" % (str(flag[0]), fjoin_nick))
									hasflag = True
							if not hasflag:
								if self.chanflag("v", fjoin_chan):
									self.mode(fjoin_chan, "+v %s" % fjoin_nick)
							if self.isoper(fjoin_nick) and self.chanexist(fjoin_chan):
								self.send(":%s NOTICE %s :Operator %s has joined" % (self.services_id, fjoin_chan, self.nick(fjoin_nick)))
								self.send(":%s PRIVMSG %s :ACTION goes down on his knee and prays to %s." % (self.bot, fjoin_chan, self.nick(fjoin_nick)))
						if data.split()[1] == "OPERTYPE":
							uid = data.split()[0][1:]
							self.query("insert into opers values ('%s')" % uid)
						if data.split()[1] == "METADATA":
							if len(data.split()) == 5 and len(data.split()[4]) != 1:
								uid = data.split()[2]
								string = data.split()[3]
								content = ' '.join(data.split()[4:])[1:]
								self.metadata(uid, string, content)
						if data.split()[1] == "UID":
							self.query("delete from temp_nick where nick = '%s'" % data.split()[2])
							self.query("insert into online values ('%s','%s')" % (data.split()[2], data.split()[4]))
		except Exception,e:
			debug("<<ERROR>> " + str(e))
			self.reconnect()

	def reconnect(self):
		try:
			self.con.close()
		except: pass
		self.run()

	def metadata(self, uid, string, content):
		if string == "accountname":
			self.query("delete from temp_nick where nick = '%s' or user = '%s'" % (uid, content))
			self.query("insert into temp_nick values ('%s','%s')" % (uid, content))
			self.msg(uid, "You are now logged in as %s" % content)
			self.vhost(uid)
			self.flag(uid)

	def omessage(self, source, text):
		try:
			cmd = text.lower().split()[0]
			arg = text.split()[1:]
			args = ' '.join(text.split()[1:])
			if self.isoper(source):
				if cmd == "help":
					self.ohelp(source, "VHOST", "{LIST|ACTIVATE|REJECT} USER")
					self.ohelp(source, "GLOBAL", "MESSAGE")
					self.ohelp(source, "FEEDBACK", "[USER]")
					self.ohelp(source, "KILL", "NICK")
					self.ohelp(source, "QUIT", "[{UPGRADE} / REASON]")
					self.ohelp(source, "VERSION")
				elif cmd == "vhost":
					if arg[0].lower() == "list":
						for data in self.query("select user,vhost from vhosts where active = '0'"):
							self.omsg(source, "User: %s\t|\tRequested vHost: %s" % (str(data[0]), str(data[1])))
					if arg[0].lower() == "activate":
						for data in self.query("select user from vhosts where active = '0'"):
							if arg[1].lower() == str(data[0]).lower():
								self.query("update vhosts set active = '1' where user = '%s'" % str(data[0]))
								for user in self.query("select nick from temp_nick where user = '%s'" % str(data[0])):
									for vhost in self.query("select vhost from vhosts where user = '%s' and active = '1'" % str(data[0])):
										self.send(":%s CHGHOST %s %s" % (self.bot, str(user[0]), str(vhost[0])))
										self.msg(str(user[0]), "Your vhost\2 %s\2 has been activated" % str(vhost[0]))
								self.omsg(source, "vHost for user \2%s\2 has been activated" % str(data[0]))
					if arg[0].lower() == "reject":
						for data in self.query("select user from vhosts where active = '0'"):
							if arg[1].lower() == str(data[0]).lower():
								self.query("delete from vhosts where user = '%s'" % str(data[0]))
								self.omsg(source, "vHost for user\2 %s\2 has been rejected" % str(data[0]))
				elif cmd == "global":
					self.omsg("$*", "[%s] " % self.nick(source) + args)
				elif cmd == "feedback":
					if len(args) == 0:
						self.omsg(source, "Following users sent a feedback:")
						for data in self.query("select user from feedback"):
							self.omsg(source, str(data[0]))
						self.omsg(source, "To read a feedback: \2FEEDBACK \37USER\37\2")
					else:
						entry = False
						for data in self.query("select user,text from feedback"):
							if arg[0].lower() == str(data[0]).lower():
								entry = True
								self.omsg(source, "\2[FEEDBACK]\2")
								self.omsg(source, "\2FROM\2: %s" % str(data[0]))
								self.omsg(source, "\2MESSAGE\2: " + str(data[1]))
								self.query("delete from feedback where user = '%s'" % str(data[0]))
						if not entry:
							self.omsg(source, "There is no feedback from\2 %s\2" % arg[0])
				elif cmd == "kill":
					if len(arg) == 1:
						self.kill(arg[0], "You're violation network rules")
					elif len(arg) > 1:
						self.kill(arg[0], ' '.join(arg[1:]))
					else:
						self.omsg(source, "Syntax: \2KILL \37NICK\37\2")
				elif cmd == "quit":
					if len(arg) == 0:
						msg = "services shutdown"
						self.send(":%s QUIT :%s" % (self.bot, msg))
						self.send(":%s QUIT :%s" % (self.obot, msg))
					elif len(arg) == 1:
						if args.lower() == "upgrade":
							msg = "we are going down for an upgrade. we are back as soon as it is finished!"
							self.send(":%s QUIT :%s" % (self.bot, msg))
							self.send(":%s QUIT :%s" % (self.obot, msg))
						else:
							self.send(":%s QUIT :%s" % (self.bot, args))
							self.send(":%s QUIT :%s" % (self.obot, args))
					else:
						self.send(":%s QUIT :%s" % (self.bot, args))
						self.send(":%s QUIT :%s" % (self.obot, args))
					self.con.close()
					sys.exit(2)
				elif cmd == "version": self.version(self.obot, source)
				else:
					self.omsg(source, "Unknown command {0}. Use HELP for more information".format(cmd.upper()))
			else:
				self.omsg(source, "I'm the Operators Service. Only IRC Operators can use me.")
		except Exception,e: print(e)

	def message(self, source, text):
		arg = text.split()
		if text.lower().split()[0] == "help":
			self.help(source, "HELP", "Shows information about all commands that are available to you")
			if self.auth(source) == 0 or self.isoper(source):
				self.help(source, "AUTH", "Authes you")
				self.help(source, "CAUTH", "Authes you with crypted data")
				self.help(source, "HELLO", "Creates an account")
			if self.auth(source) != 0 or self.isoper(source):
				self.help(source, "NEWPASS", "Changes your password")
				self.help(source, "VHOST", "Requests a vHost for your Account")
				self.help(source, "REQUEST", "Request for a channel")
				self.help(source, "CHANLEV", "Edits your channel records")
				self.help(source, "CHANMODE", "Sets modes for your channel")
				self.help(source, "CHANFLAGS", "Sets flags for your channel")
				self.help(source, "SETTOPIC", "Sets topic for your channel")
				self.help(source, "FEEDBACK", "Sends a feedback to us")
				self.help(source, "WHOIS", "Shows information about a user")
			self.help(source, "VERSION", "Shows version of services")
		elif arg[0].lower() == "newpass" and self.auth(source) != 0:
			if len(arg) == 2:
				self.query("update users set pass = '%s' where name = '%s'" % (self.hash(arg[1]), self.auth(source)))
				self.msg(source, """Your new password is "%s". Remember it!""" % arg[1])
			else:
				self.msg(source, "Syntax: NEWPASS \37password\37")
		elif arg[0].lower() == "hello" and self.auth(source) == 0:
			if len(arg) == 3:
				exists = False
				for data in self.query("select name from users where email = '%s' or name = '%s'" % (arg[1], self.nick(source))):
						exists = True
				if not exists:
					if arg[1].find("@") != -1 and arg[1].find(".") != -1 and arg[1].lower() == arg[2].lower():
						self.query("insert into users values ('%s','%s','%s')" % (self.nick(source), self.hash(hash(arg[1])), arg[1]))
						self.msg(source, "The account %s has been created successfully. You can login now with /msg Q auth account password" % self.nick(source))
						sender = self.email
						receivers = ['%s' % arg[1]]
						if self.regmail == "1":
							self.msg(source, "An email had been send to you with your password!")
							self.mail(arg[1], """From: %s <%s>\nTo: %s <%s>\nSubject: Your account on %s\n\nWelcome to %s\nYour account data:\n\nUser: %s\nPassword: %s\n\nAuth via "/msg Q auth %s %s"\nChange your password as soon as possible with "/msg Q newpass NEWPASS"!""" % (self.services_description, self.email, self.nick(source), arg[1], self.services_description, self.services_description, self.nick(source), hash(arg[1]), self.nick(source), hash(arg[1])))
						else:
							self.msg(source, """Use "/msg Q auth %s %s" to auth""" % (self.nick(source), hash(arg[1])))
							self.msg(source, "Change your password as soon as possible!")
					else:
						self.msg(source, "Invalid email %s!" % arg[1])
				else:
					self.msg(source, "The account %s already exists or your email %s is used!" % (self.nick(source),arg[1]))
			else:
				self.msg(source, "Syntax: HELLO \37email\37 \37email\37")
		elif text.lower().split()[0] == "auth" and self.auth(source) == 0:
			if len(text.split()) == 3:
				exists = False
				for data in self.query("select name,pass from users where name = '%s'" % text.split()[1]):
					if self.hash(text.split()[2]) == str(data[1]):
						exists = True
						for user in self.query("select nick from temp_nick where user = '%s'" % str(data[0])):
							self.msg(str(user[0]), "Someone else has authed with your account")
						self.query("insert into temp_nick values ('%s','%s')" % (source, str(data[0])))
						self.msg(source, "You are now logged in as %s" % str(data[0]))
						self.meta(source, "accountname", str(data[0]))
						self.vhost(source)
						self.flag(source)
				if not exists:
					self.msg(source, "Wrong username or invalid password.")
			else:
				self.msg(source, "Syntax: AUTH \37account\37 \37password\37")
		elif arg[0].lower() == "cauth" and self.auth(source) == 0:
			if len(arg) == 2:
				exists = False
				for data in self.query("select name,pass from users where name = '%s'" % arg[1].split(":")[0]):
					md5 = hashlib.md5()
					md5.update(str(data[1]))
					if str(md5.hexdigest()) == arg[1].split(":")[1]:
						exists = True
						for user in self.query("select nick from temp_nick where user = '%s'" % str(data[0])):
							self.msg(str(user[0]), "Someone else has authed with your account")
						self.query("insert into temp_nick values ('%s','%s')" % (source, str(data[0])))
						self.msg(source, "You are now logged in as %s" % str(data[0]))
						self.meta(source, "accountname", str(data[0]))
						self.vhost(source)
						self.flag(source)
				if not exists:
					self.msg(source, "Cauth failed.")
			else:
				self.msg(source, "Syntax: CAUTH \37USERNAME\37:\37SHA1-MD5-HASHED-PASSWORD\37")

		elif text.lower().split()[0] == "vhost" and self.auth(source) != 0:
			if len(text.split()) == 2:
				self.query("delete from vhosts where user = '%s'" % self.auth(source))
				self.query("insert into vhosts values ('%s','%s','0')" % (self.auth(source), text.split()[1]))
				self.msg(source, "Your new vhost\2 %s\2 has been requested" % text.split()[1])
				self.vhost(source)
			else:
				self.msg(source, "Syntax: VHOST \37vhost\37")
		elif text.lower().split()[0] == "request" and self.auth(source) != 0:
			if len(text.split()) == 2 and text.split()[1].startswith("#"):
				exists = False
				for data in self.query("select channel from channels"):
					if text.lower().split()[1] == str(data[0]).lower():
						exists = True
				if not exists:
					self.query("insert into channelinfo values ('%s', '', '', '')" % text.split()[1])
					self.query("insert into channels values ('%s','%s','n')" % (text.split()[1], self.auth(source)))
					self.join(text.split()[1])
					self.msg(source, "Channel \2%s\2 has been registered for you" % text.split()[1])
				else:
					self.msg(source, "Channel \2%s\2 is already registered" % text.split()[1])
			else:
				self.msg(source, "An error has happened while registering channel \2%s\2 for you, %s." % (text.split()[1], self.auth(source)))
		elif arg[0].lower() == "chanlev" and self.auth(source) != 0:
			if len(arg) == 2:
				channel = text.split()[1]
				for data in self.query("select * from channels"):
					content = str(data[0])
					user = str(data[1])
					flag = str(data[2])
					if channel.lower() == content.lower():
						self.msg(source, "[%s] User: %s\t||\tFlag: %s" % (content, user, flag))
			if len(arg) == 4:
				channel = text.split()[1]
				entry = False
				for channels in self.query("select channel from channels where user = '%s' and flag = 'n'" % self.auth(source)):
					if channel.lower() == str(channels[0]).lower():
						entry = True
						channel = str(channels[0])
				if entry:
					user = False
					for data in self.query("select name from users"):
						if text.lower().split()[2] == str(data[0]).lower():
							username = str(data[0])
							user = True
					if user and str(self.auth(source)).lower() != username.lower():
						self.query("delete from channels where channel = '%s' and user = '%s'" % (channel, username))
						self.query("insert into channels values ('%s','%s','%s')" % (channel, username, text.split()[3]))
						self.msg(source, "[%s] %s has been with mode +%s" % (channel, username, text.split()[3]))
					else: self.msg(source, "An error has happened")
				else: self.msg(source, "An error has happened")
		elif arg[0].lower() == "chanmode" and self.auth(source) != 0:
			if len(arg) == 2:
				if arg[1].startswith("#"):
					if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "a":
						for channel in self.query("select name,modes from channelinfo where name = '{0}'".format(arg[1])):
							self.msg(source, "Current modes for {0}: {1}".format(channel[0], channel[1]))
					else:
						self.msg(source, "No permission")
				else:
					self.msg(source, "Invalid channel '{0}'".format(arg[1]))
			elif len(arg) == 3:
				if arg[1].startswith("#"):
					if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "a":
						for channel in self.query("select name from channelinfo where name = '{0}'".format(arg[1])):
							self.query("update channelinfo set modes = '{0}' where name = '{1}'".format(arg[2], channel[0]))
							self.mode(channel[0], arg[2])
							self.msg(source, "New modes for {0}: {1}".format(channel[0], arg[2]))
					else:
						self.msg(source, "No permission")
				else:
					self.msg(source, "Invalid channel '{0}'".format(arg[1]))
			else:
				self.msg(source, "Syntax: \2CHANMODE\2 \37#channel\37 [\37modes\37]")
		elif arg[0].lower() == "chanflags" and self.auth(source) != 0:
			if len(arg) == 2:
				if arg[1].startswith("#"):
					if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "a":
						for channel in self.query("select name,flags from channelinfo where name = '{0}'".format(arg[1])):
							self.msg(source, "Current flags for {0}: {1}".format(channel[0], channel[1]))
					else:
						self.msg(source, "No permission")
				else:
					self.msg(source, "Invalid channel '{0}'".format(arg[1]))
			elif len(arg) == 3:
				if arg[1].startswith("#"):
					if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "a":
						for channel in self.query("select name from channelinfo where name = '{0}'".format(arg[1])):
							self.query("update channelinfo set flags = '{0}' where name = '{1}'".format(arg[2], channel[0]))
							self.msg(source, "New flags for {0}: {1}".format(channel[0], arg[2]))
					else:
						self.msg(source, "No permission")
				else:
					self.msg(source, "Invalid channel '{0}'".format(arg[1]))
			else:
				self.msg(source, "Syntax: \2CHANFLAGS\2 \37#channel\37 [\37flags\37]")
		elif arg[0].lower() == "settopic" and self.auth(source) != 0:
			if len(arg) > 2:
				if arg[1].startswith("#"):
					if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "a":
						self.query("update channelinfo set topic = '{0}' where name = '{1}'".format(' '.join(arg[2:]), arg[1]))
						self.send(":{0} TOPIC {1} :{2}".format(self.bot, arg[1], ' '.join(arg[2:])))
						self.msg(source, "Done.")
					else: self.msg(source, "No permission")
				else: self.msg(source, "Invalid channel '{0}'".format(arg[1]))
			elif len(arg) == 2:
				if arg[1].startswith("#"):
					if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "a":
						for channel in self.query("select name,topic from channelinfo where name = '{0}'".format(arg[1])):
							self.msg(source, "Current topic for {0}: {1}".format(channel[0], channel[1]))
					else: self.msg(source, "No permission")
				else: self.msg(source, "Invalid channel '{0}'".format(arg[1]))
			else: self.msg(source, "Syntax: \2SETTOPIC\2 \37#channel\37 [\37topic\37]")
		elif arg[0].lower() == "feedback" and self.auth(source) != 0:
			if len(arg) > 1:
				entry = False
				for data in self.query("select text from feedback where user = '%s'" % self.auth(source)):
					entry = True
				if not entry:
					try:
						self.query("insert into feedback values('"+self.auth(source)+"','"+' '.join(arg[1:])+"')")
						self.msg(source, "Feedback added to queue.")
						for op in self.query("select uid from opers"):
							self.omsg(str(op[0]), "New feedback from\2 %s\2" % self.auth(source))
					except Exception,e:
						self.msg(source, e)
				else:
					self.msg(source, "You already sent a feedback. Please wait until an operator read it.")
			else:
				self.msg(source, "\2FEEDBACK\2 \37TEXT\37")
		elif arg[0].lower() == "whois" and self.auth(source) != 0:
			entry = False
			if len(arg) == 2:
				if arg[1].startswith("#"):
					for user in self.query("select name,email from users where name = '{0}'".format(arg[1][1:])):
						entry = True
						self.msg(source, "-Information for account {0}:".format(user[0]))
						online = list()
						for uid in self.query("select nick from temp_nick where user = '{0}'".format(user[0])):
							for data in self.query("select nick from online where uid = '{0}'".format(uid[0])):
								online.append(data[0])
						self.msg(source, "Online Nicks: {0}".format(' '.join(online)))
						self.msg(source, "Email address: {0}".format(user[1]))
						self.msg(source, "Known on following channels:")
						self.msg(source, "Channel              Flag")
						for channel in self.query("select channel,flag from channels where user = '{0}'".format(user[0])):
							self.msg(source, " {0}{1}{2}".format(channel[0], " "*int(20-len(channel[0])), channel[1]))
						self.msg(source, "End of list.")
				else:
					for data in self.query("select uid from online where nick = '{0}'".format(arg[1])):
						entry = True
						for user in self.query("select user from temp_nick where nick = '{0}'".format(data[0])):
							for account in self.query("select email from users where name = '{0}'".format(user[0])):
								self.msg(source, "-Information for account {0}:".format(user[0]))
								online = list()
								for uid in self.query("select nick from temp_nick where user = '{0}'".format(user[0])):
									for online_data in self.query("select nick from online where uid = '{0}'".format(uid[0])):
										online.append(online_data[0])
								self.msg(source, "Online Nicks: {0}".format(' '.join(online)))
								self.msg(source, "Email address: {0}".format(account[0]))
								self.msg(source, "Known on following channels:")
								self.msg(source, "Channel              Flag")
							for channel in self.query("select channel,flag from channels where user = '{0}'".format(user[0])):
								self.msg(source, " {0}{1}{2}".format(channel[0], " "*int(20-len(channel[0])), channel[1]))
							self.msg(source, "End of list.")
				if not entry:
					self.msg(source, "Can\'t find user {0}".format(arg[1]))
			else:
				self.msg(source, "Syntax: \2WHOIS\2 \37NICK/#ACCOUNT\37")
		elif arg[0].lower() == "version": self.version(self.bot, source)
		else:
			self.msg(source, "Unknown command {0}. Please try HELP for more information.".format(arg[0].upper()))

	def nick (self, source):
		for data in self.query("select nick from online where uid = '%s'" % source):
			return str(data[0])

	def send(self, text):
		self.con.send(text+"\n")
		debug(">> %s" % text)

	def help(self, target, command, description=""):
		self.msg(target, command.upper()+" "*int(20-len(command))+description)

	def ohelp(self, target, command, description=""):
		self.omsg(target, command.upper()+" "*int(20-len(command))+description)

	def msg(self, target, text):
		self.send(":%s NOTICE %s :%s" % (self.bot, target, text))

	def omsg(self, target, text):
		self.send(":%s NOTICE %s :%s" % (self.obot, target, text))

	def mode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.bot, target, mode))

	def omode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.obot, target, mode))

	def smode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.services_id, target, mode))

	def meta(self, target, meta, content):
		self.send(":%s METADATA %s %s :%s" % (self.services_id, target, meta, content))

	def auth(self, target):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			return str(data[0])
		return 0

	def chanexist(self, channel):
		for data in self.query("select name from channelinfo where name = '%s'" % channel):
			return True
		return False

	def join(self, channel):
		self.send(":%s JOIN %s" % (self.bot, channel))
		self.smode(channel, "+q %s" % self.bot)

	def ojoin(self, channel):
		self.send(":%s JOIN %s" % (self.obot, channel))
		self.smode(channel, "+q %s" % self.obot)

	def kill(self, target, reason):
		if target.lower() != "o" and target.lower() != "q":
			self.send(":%s KILL %s :Killed (%s (%s))" % (self.obot, target, self.services_name, reason))

	def vhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
			self.send(":%s CHGHOST %s %s" % (self.bot, target, str(data[0])))
			self.msg(target, "Your vhost\2 %s\2 has been activated" % str(data[0]))

	def version(self, source, target):
		self.send(":%s NOTICE %s :PyServ v%s" % (source, target, __version__))
		self.send(":%s NOTICE %s :Uptime: %s" % (source, target, self.convert_timestamp(time.time() - _started)))
		self.send(":%s NOTICE %s :Running on: %s %s %s" % (source, target, os.uname()[0], os.uname()[2], os.uname()[-1]))

	def flag(self, target):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag,channel from channels where user = '%s'" % str(data[0])):
				if str(flag[0]) == "n":
					self.mode(str(flag[1]), "+q %s" % target)
				elif str(flag[0]) == "Y":
					pass
				else:
					self.mode(str(flag[1]), "+%s %s" % (str(flag[0]), target))

	def getflag(self, target, channel):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (channel, data[0])):
				return flag[0]
		return 0

	def chanflag(self, flag, channel):
		for data in self.query("select flags from channelinfo where name = '{0}'".format(channel)):
			if data[0].find(flag) != -1:
				return True
		return False

	def isoper(self, target):
		isoper = False
		for data in self.query("select * from opers where uid = '%s'" % target):
			isoper = True 
		return isoper

	def hash(self, string):
		sha1 = hashlib.sha1()
		sha1.update(str(string))
		return str(sha1.hexdigest())

	def query(self, string):
		self.db.query(str(string))
		result = self.db.store_result()
		try:
			return result.fetch_row(maxrows=0)
		except: pass

	def mail(self, receiver, message):
		mail = smtplib.SMTP('127.0.0.1', 25)
		mail.sendmail(self.email, ['%s' % receiver], message)
		mail.quit()

	def convert_timestamp(self, timestamp):
		dif = int(timestamp)
		days = 0
		hours = 0
		minutes = 0
		seconds = 0
		if dif == 86400 or dif > 86400:
			days = int(dif)/86400
			dif = int(dif)-int(days)*86400
		if dif == 3600 or dif > 3600:
			hours = int(dif)/3600
			dif = int(dif)-int(hours)*3600
		if dif == 60 or dif > 60:
			minutes = int(dif)/60
			dif = int(dif)-int(minutes)*60
		seconds = dif
		if days > 0: return "%s days %s hours %s minutes %s seconds" % (days, hours, minutes, seconds)
		if hours > 0: return "%s hours %s minutes %s seconds" % (hours, minutes, seconds)
		if minutes > 0: return "%s minutes %s seconds" % (minutes, seconds)
		return "%s seconds" % seconds

if __name__ == "__main__":
	try:
		Services().run()
	except Exception,e: print(e)
	except KeyboardInterrupt: print("Aborting ... STRG +C")
