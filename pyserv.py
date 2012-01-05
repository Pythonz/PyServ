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
		self.db = sqlite3.connect("data.db")
		self.db.isolation_level = None

	def run(self):
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
						if data.split()[1] == "PING":
							self.send(":%s PONG %s %s" % (self.services_id, self.services_id, data.split()[2]))
							self.send(":%s PING %s %s" % (self.services_id, self.services_id, data.split()[2]))
						if data.split()[1] == "ENDBURST":
							self.send(":%s UID %s %s Q %s %s TheQBot 0.0.0.0 %s +IO :The Q Bot" % (self.services_id, self.bot, time.time(), self.services_name, self.services_name, time.time()))
							self.join("#opers")
							for channel in self.db.execute("select name from chanlist"):
								self.join(str(channel[0]))
							self.mode("#opers", "+q %s %s" % (self.bot, self.bot))
							self.meta(self.bot, "accountname", "Q")
						if data.split()[1] == "PRIVMSG" and data.split()[2] == self.bot:
							self.message(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
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
							fjoin_user = self.auth(fjoin_nick)
							for flag in self.db.execute("select flag from channels where channel = '%s' and user = '%s'" % (fjoin_chan, fjoin_user)):
								if str(flag[0]) == "n":
									self.mode(fjoin_chan, "+q %s" % fjoin_nick)
								elif str(flag[0]) == "Y":
									pass
								else:
									self.mode(fjoin_chan, "+%s %s" % (str(flag[0]), fjoin_nick))

	def message(self, source, text):
		arg = text.split()
		if text.lower().split()[0] == "showcommands":
			self.msg(source, "SHOWCOMMANDS - Shows information about all commands that are available to you")
			self.msg(source, "AUTH - Authes you")
			self.msg(source, "HELLO - Creates a account")
			self.msg(source, "VHOST - Request your vHost")
			self.msg(source, "REQUEST - Request for a channel")
			self.msg(source, "CHANLEV - Edits your channel records")
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
							
		else:
			self.msg(source, "Unknown command. Please try 'SHOWCOMMANDS' for more information.")

	def send(self, text):
		self.con.send(text+"\n")
		debug(">> %s" % text)

	def msg(self, target, text):
		self.send(":%s NOTICE %s :%s" % (self.bot, target, text))

	def mode(self, target, mode):
		self.send(":%s MODE %s %s" % (self.bot, target, mode))

	def meta(self, target, meta, content):
		self.send(":%s METADATA %s %s :%s" % (self.services_id, target, meta, content))

	def auth(self, target):
		for data in self.db.execute("select user from temp_nick where nick = '%s'" % target):
			return str(data[0])
		return 0

	def join(self, channel):
		self.send(":%s JOIN %s" % (self.bot, channel))
		self.mode(channel, "+q %s" % self.bot)

	def vhost(self, target):
		for data in self.db.execute("select vhost from vhosts where user = '%s'" % self.auth(target)):
			self.send(":%s CHGHOST %s %s" % (self.bot, target, str(data[0])))
			self.msg(target, "Your vhost\2 %s\2 has been activated" % str(data[0]))

Services().run()
