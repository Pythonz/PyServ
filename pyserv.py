#!/usr/bin/env python

import sys, socket, sqlite3, os, thread, ConfigParser, time

config = ConfigParser.RawConfigParser()
config.read("pyserv.conf")

def debug(text):
	if config.get("OTHER", "debug") == "1":
		print(str(text))

class Services:
	def __init__(self):
		self.server_name = config.get("SERVER", "name")
		self.server_address = config.get("SERVER", "address")
		self.server_port = config.get("SERVER", "port")
		self.server_id = config.get("SERVER", "id")
		self.server_password = config.get("SERVER", "password")
		self.services_name = config.get("SERVICES", "name")
		self.services_id = config.get("SERVICES", "id")
		self.services_description = config.get("SERVICES", "description")
		self.debug = config.get("OTHER", "debug")
		self.bot = "%sAAAAAA" % self.services_id
		self.obot = "%sAAAAAB" % self.services_id
		self.db = sqlite3.connect("data.db")
		self.db.isolation_level = None

	def run(self):
		self.db.execute("delete from temp_nick")
		self.db.execute("delete from opers")
		self.con = socket.socket()
		self.con.connect((self.server_address, int(self.server_port)))
		self.send("SERVER %s %s 0 %s :%s" % (self.services_name, self.server_password, self.services_id, self.services_description))
		self.send(":%s BURST" % self.services_id)
		self.send(":%s ENDBURST" % self.services_id)
		
		while 1:
			recv = self.con.recv(4096)
			if recv != "":
				for data in recv.rstrip().split("\n"):
					debug("<< %s" % data)
					if data.startswith("ERROR :"):
						self.db.execute("delete from temp_nick")
						self.con.close()
					if len(data.split()) != 0:
						if data.split()[1] == "ERROR":
							self.db.execute("delete from temp_nick")
							self.con.close()
						if data.split()[1] == "PING":
							self.send(":%s PONG %s %s" % (self.services_id, self.services_id, data.split()[2]))
							self.send(":%s PING %s %s" % (self.services_id, self.services_id, data.split()[2]))
						if data.split()[1] == "ENDBURST":
							self.send(":%s UID %s %s Q %s %s TheQBot 0.0.0.0 %s +I :The Q Bot" % (self.services_id, self.bot, time.time(), self.services_name, self.services_name, time.time()))
							self.send(":%s OPERTYPE IRC" % self.bot)
							self.join("#opers")
							self.mode("#opers", "+q %s" % self.bot)
							self.meta(self.bot, "accountname", "Q")
							self.send(":%s UID %s %s O %s %s TheOBot 0.0.0.0 %s +I :The O Bot" % (self.services_id, self.obot, time.time(), self.services_name, self.services_name, time.time()))
							self.send(":%s OPERTYPE IRC" % self.obot)
							self.ojoin("#opers")
							self.omode("#opers", "+q %s" % self.obot)
							self.meta(self.obot, "accountname", "O")
							self.omsg("$*", "Services are back online. Have a nice day :)")
							for channel in self.db.execute("select name from chanlist"):
								self.join(str(channel[0]))
						if data.split()[1] == "PRIVMSG":
							if data.split()[2] == self.bot:
								self.message(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
							if data.split()[2] == self.obot:
								self.omessage(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
						if data.split()[1] == "QUIT":
							self.db.execute("delete from temp_nick where nick = '%s'" % str(data.split()[0])[1:])
						if data.split()[1] == "FMODE":
							if len(data.split()) > 5:
								for user in data.split()[6:]:
									for flag in self.db.execute("select flag from channels where channel = '%s' and user = '%s'" % (data.split()[2], self.auth(user))):
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
							for flag in self.db.execute("select flag from channels where channel = '%s' and user = '%s'" % (fjoin_chan, fjoin_user)):
								if str(flag[0]) == "n":
									self.mode(fjoin_chan, "+q %s" % fjoin_nick)
								elif str(flag[0]) == "Y":
									pass
								else:
									self.mode(fjoin_chan, "+%s %s" % (str(flag[0]), fjoin_nick))
						if data.split()[1] == "OPERTYPE":
							uid = data.split()[0][1:]
							self.db.execute("insert into opers values ('%s')" % uid)
						if data.split()[1] == "METADATA":
							uid = data.split()[2]
							string = data.split()[3]
							content = ' '.join(data.split()[4:])[1:]
							self.metadata(uid, string, content)

	def metadata(self, uid, string, content):
		if string == "accountname":
			self.db.execute("delete from temp_nick where nick = '%s' or user = '%s'" % (uid, content))
			self.db.execute("insert into temp_nick values ('%s','%s')" % (uid, content))
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
					self.omsg(source, "VHOST \37{LIST|ACTIVATE|REJECT}\37 USER")
					self.omsg(source, "GLOBAL \37\2MESSAGE\2\37")
					self.omsg(source, "FEEDBACK [READ \37user\37]")
				elif cmd == "vhost":
					if arg[0].lower() == "list":
						for data in self.db.execute("select user,vhost from vhosts where active = '0'"):
							self.omsg(source, "User: %s\t|\tRequested vHost: %s" % (str(data[0]), str(data[1])))
					if arg[0].lower() == "activate":
						for data in self.db.execute("select user from vhosts where active = '0'"):
							if arg[1].lower() == str(data[0]).lower():
								self.db.execute("update vhosts set active = '1' where user = '%s'" % str(data[0]))
								for user in self.db.execute("select nick from temp_nick where user = '%s'" % str(data[0])):
									for vhost in self.db.execute("select vhost from vhosts where user = '%s' and active = '1'" % str(data[0])):
										self.send(":%s CHGHOST %s %s" % (self.bot, str(user[0]), str(vhost[0])))
										self.msg(str(user[0]), "Your vhost\2 %s\2 has been activated" % str(vhost[0]))
								self.omsg(source, "vHost for user \2%s\2 has been activated" % str(data[0]))
					if arg[0].lower() == "reject":
						for data in self.db.execute("select user from vhosts where active = '0'"):
							if arg[1].lower() == str(data[0]).lower():
								self.db.execute("delete from vhosts where user = '%s'" % str(data[0]))
								self.omsg(source, "vHost for user \2%s\2 has been rejected" % str(data[0]))
				elif cmd == "global":
					self.omsg("$*", args)
				elif cmd == "feedback":
					if len(args) == 0:
						self.omsg(source, "Following users sent a feedback:")
						for data in self.db.execute("select user from feedback"):
							self.omsg(source, str(data[0]))
						self.omsg(source, "To read a feedback: \2FEEDBACK \37USER\37")
					else:
						entry = False
						for data in self.db.execute("select user,text from feedback"):
							if arg[0].lower() == str(data[0]).lower():
								entry = True
								self.omsg(source, "\2[FEEDBACK]\2")
								self.omsg(source, "\2FROM\2: %s" % str(data[0]))
								self.omsg(source, "\2MESSAGE\2: %s" % str(data[1]))
								self.db.execute("delete from feedback where user = '%s'" % str(data[0]))
						if not entry:
							self.omsg(source, "There is no feedback from\2 %s\2" % arg[0])
				else:
					self.omsg(source, "Unknown command. Use 'HELP' for more information")
			else:
				self.omsg(source, "I'm the Operators Service. Only IRC Operators can use me.")
		except Exception,e: print(e)

	def message(self, source, text):
		arg = text.split()
		if text.lower().split()[0] == "help":
			self.msg(source, "HELP - Shows information about all commands that are available to you")
			self.msg(source, "AUTH - Authes you")
			self.msg(source, "HELLO - Creates a account")
			self.msg(source, "VHOST - Request your vHost")
			self.msg(source, "REQUEST - Request for a channel")
			self.msg(source, "CHANLEV - Edits your channel records")
			self.msg(source, "FEEDBACK - Sends your feedback to us")
		elif text.lower().split()[0] == "hello":
			if len(text.split()) == 3:
				exists = False
				for data in self.db.execute("select name from users"):
					if str(text.split()[1]).lower() == str(data[0]).lower():
						exists = True
				if not exists:
					if len(text.split()[2]) > 5:
						self.db.execute("insert into users values ('%s','%s')" % (text.split()[1], text.split()[2]))
						self.msg(source, "The account %s has been created successfully. You can login now with /msg Q auth account password" % text.split()[1])
					else:
						self.msg(source, "Your password is too short!")
				else:
					self.msg(source, "The account %s already exists!" % text.split()[1])
			else:
				self.msg(source, "Syntax: HELLO \37account\37 \37password\37")
		elif text.lower().split()[0] == "auth":
			if self.auth(source) == 0:
				if len(text.split()) == 3:
					exists = False
					for data in self.db.execute("select name,pass from users"):
						if str(text.split()[1]).lower() == str(data[0]).lower():
							if str(text.split()[2]) == str(data[1]):
								exists = True
								for user in self.db.execute("select nick from temp_nick where user = '%s'" % str(data[0])):
									self.msg(str(user[0]), "Someone else has authed with your account")
								self.db.execute("delete from temp_nick where nick = '%s' or user = '%s'" % (source, str(data[0])))
								self.db.execute("insert into temp_nick values ('%s','%s')" % (source, str(data[0])))
								self.msg(source, "You are now logged in as %s" % str(data[0]))
								self.meta(source, "accountname", str(data[0]))
								self.vhost(source)
								self.flag(source)
					if not exists:
						self.msg(source, "Wrong username or invalid password.")
				else:
					self.msg(source, "Syntax: AUTH \37account\37 \37password\37")
			else:
				self.msg(source, "Auth is not available once you are authed")
		elif text.lower().split()[0] == "vhost":
			if self.auth(source) != 0 and len(text.split()) == 2:
				self.db.execute("delete from vhosts where user = '%s'" % self.auth(source))
				self.db.execute("insert into vhosts values ('%s','%s','0')" % (self.auth(source), text.split()[1]))
				self.msg(source, "Your new vhost\2 %s\2 has been requested" % text.split()[1])
				self.vhost(source)
			else:
				self.msg(source, "You are not authed")
		elif text.lower().split()[0] == "request":
			if self.auth(source) != 0 and len(text.split()) == 2 and text.split()[1].startswith("#"):
				exists = False
				for data in self.db.execute("select channel from channels"):
					if text.lower().split()[1] == str(data[0]).lower():
						exists = True
				if not exists:
					self.db.execute("insert into chanlist values ('%s')" % text.split()[1])
					self.db.execute("insert into channels values ('%s','%s','n')" % (text.split()[1], self.auth(source)))
					self.join(text.split()[1])
					self.msg(source, "Channel \2%s\2 has been registered for you" % text.split()[1])
				else:
					self.msg(source, "Channel \2%s\2 is already registered" % text.split()[1])
			else:
				self.msg(source, "An error has happened while registering channel \2%s\2 for you, %s." % (text.split()[1], self.auth(source)))
		elif arg[0].lower() == "chanlev":
			if len(arg) == 2:
				channel = text.split()[1]
				for data in self.db.execute("select * from channels"):
					content = str(data[0])
					user = str(data[1])
					flag = str(data[2])
					if channel.lower() == content.lower():
						self.msg(source, "[%s] User: %s\t||\tFlag: %s" % (content, user, flag))
			if self.auth(source) != 0:
				if len(arg) == 4:
					channel = text.split()[1]
					entry = False
					for channels in self.db.execute("select channel from channels where user = '%s' and flag = 'n'" % self.auth(source)):
						if channel.lower() == str(channels[0]).lower():
							entry = True
							channel = str(channels[0])
					if entry:
						user = False
						for data in self.db.execute("select name from users"):
							if text.lower().split()[2] == str(data[0]).lower():
								username = str(data[0])
								user = True
						if user and str(self.auth(source)).lower() != username.lower():
							self.db.execute("delete from channels where channel = '%s' and user = '%s'" % (channel, username))
							self.db.execute("insert into channels values ('%s','%s','%s')" % (channel, username, text.split()[3]))
							self.msg(source, "[%s] %s has been with mode +%s" % (channel, username, text.split()[3]))
						else: self.msg(source, "An error has happened")
					else: self.msg(source, "An error has happened")
			else: self.msg(source, "You are not authed")
		elif arg[0].lower() == "feedback":
			if self.auth(source) != 0:
				if len(arg) > 1:
					entry = False
					for data in self.db.execute("select text from feedback where user = '%s'" % self.auth(source)):
						entry = True
					if not entry:
						self.db.execute("insert into feedback values('%s','%s')" % (self.auth(source), ' '.join(arg[1:])))
						self.msg(source, "Feedback added to queue.")
						for op in self.db.execute("select uid from opers"):
							self.omsg(str(op[0]), "New feedback from\2 %s\2" % self.auth(source))
					else:
						self.msg(source, "You already sent a feedback. Please wait until an operator read it.")
				else:
					self.msg(source, "\2FEEDBACK\2 \37TEXT\37")
			else:
				self.msg(source, "You have to be logged in to use this function")
		else:
			self.msg(source, "Unknown command. Please try 'HELP' for more information.")

	def send(self, text):
		self.con.send(text+"\n")
		debug(">> %s" % text)

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
		for data in self.db.execute("select user from temp_nick where nick = '%s'" % target):
			return str(data[0])
		return 0

	def join(self, channel):
		self.send(":%s JOIN %s" % (self.bot, channel))
		self.smode(channel, "+q %s" % self.bot)

	def ojoin(self, channel):
		self.send(":%s JOIN %s" % (self.obot, channel))
		self.smode(channel, "+q %s" % self.obot)

	def vhost(self, target):
		for data in self.db.execute("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
			self.send(":%s CHGHOST %s %s" % (self.bot, target, str(data[0])))
			self.msg(target, "Your vhost\2 %s\2 has been activated" % str(data[0]))

	def flag(self, target):
		for data in self.db.execute("select user from temp_nick where nick = '%s'" % target):
			for flag in self.db.execute("select flag,channel from channels where user = '%s'" % str(data[0])):
				if str(flag[0]) == "n":
					self.mode(str(flag[1]), "+q %s" % target)
				elif str(flag[0]) == "Y":
					pass
				else:
					self.mode(str(flag[1]), "+%s %s" % (str(flag[0]), target))

	def isoper(self, target):
		isoper = False
		for data in self.db.execute("select * from opers where uid = '%s'" % target):
			isoper = True 
		return isoper
try:
	Services().run()
except Exception,e: print(e)
except KeyboardInterrupt: print("Aborting ... STRG +C")
