#!/usr/bin/env python

import sys
import socket
import os
import ConfigParser
import time
import hashlib
import smtplib
import _mysql
import subprocess
import urllib2
import traceback

try:
	if not os.access("logs", os.F_OK):
		os.mkdir("logs")
	i = 1
	f = open("version", "r")
	__version__ = f.read()
	f.close()
	_updates = 0
	for doc in os.listdir("sql/updates"):
		_updates += 1
	_started = time.time()
	config = ConfigParser.RawConfigParser()
	config.read("pyserv.conf")
except Exception:
	et, ev, tb = sys.exc_info()
	print("<<ERROR>> {0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb)))

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
							self.meta(self.bot, "accountname", "Q")
							self.send(":%s UID %s %s O %s %s TheOBot 0.0.0.0 %s +I :The O Bot" % (self.services_id, self.obot, time.time(), self.services_name, self.services_name, time.time()))
							self.send(":%s OPERTYPE Service" % self.obot)
							self.meta(self.obot, "accountname", "O")
							self.omsg("$*", "Services are now back online. Have a nice day :)")
							self.version(self.obot, "$*")
							for channel in self.query("select name,modes,topic from channelinfo"):
								self.join(str(channel[0]))
								if self.chanflag("m", channel[0]):
									self.mode(channel[0], channel[1])
								if self.chanflag("t", channel[0]):
									self.send(":{0} TOPIC {1} :{2}".format(self.bot, channel[0], channel[2]))
									if self.chanflag("l", channel[0]): self.log("Q", "topic", channel[0], ":"+channel[2])
						if data.split()[1] == "PRIVMSG":
							if data.split()[2] == self.bot:
								self.message(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
							if data.split()[2] == self.obot:
								self.omessage(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "privmsg", data.split()[2], ' '.join(data.split()[3:]))
						if data.split()[1] == "NOTICE":
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "notice", data.split()[2], ' '.join(data.split()[3:]))
						if data.split()[1] == "NICK":
							self.query("update online set nick = '%s' where uid = '%s'" % (data.split()[2], str(data.split()[0])[1:]))
						if data.split()[1] == "QUIT":
							self.query("delete from temp_nick where nick = '%s'" % str(data.split()[0])[1:])
							self.query("delete from online where uid = '%s'" % str(data.split()[0])[1:])
						if data.split()[1] == "TOPIC":
							if len(data.split()) > 1:
								if self.chanflag("l", data.split()[2]): self.log(data.split()[0][1:], "topic", data.split()[2], ' '.join(data.split()[3:]))
								if self.chanflag("t", data.split()[2]):
									for channel in self.query("select topic from channelinfo where name = '{0}'".format(data.split()[2])):
										self.send(":{0} TOPIC {1} :{2}".format(self.bot, data.split()[2], channel[0]))
										if self.chanflag("l", data.split()[2]): self.log("Q", "topic", data.split()[2], ":"+channel[0])
						if data.split()[1] == "FMODE":
							if self.chanflag("m", data.split()[2]):
								if data.split()[2].startswith("#"):
									if self.chanflag("l", data.split()[2]): self.log(data.split()[0][1:], "mode", data.split()[2], ' '.join(data.split()[4:]))
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
							if self.chanflag("l", fjoin_chan):
								self.showlog(fjoin_nick, fjoin_chan)
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
							for welcome in self.query("select name,welcome from channelinfo where name = '{0}'".format(fjoin_chan)):
								if self.chanflag("w", fjoin_chan):
									self.msg(fjoin_nick, "[{0}] {1}".format(welcome[0], welcome[1]))
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
						if data.split()[1] == "IDLE":
							if len(data.split()) == 3:
								self.send(":{uid} IDLE {source} 0 0".format(uid=data.split()[2], source=data.split()[0][1:]))
						if data.split()[1] == "UID":
							self.query("delete from temp_nick where nick = '%s'" % data.split()[2])
							self.query("insert into online values ('%s','%s','%s')" % (data.split()[2], data.split()[4], data.split()[8]))
							conns = 0
							nicks = list()
							for connection in self.query("select nick from online where address = '%s'" % data.split()[8]):
								nicks.append(connection[0])
								conns += 1
							limit = 3
							for trust in self.query("select `limit` from trust where address = '%s'" % data.split()[8]):
								limit = int(trust[0])
							if conns > limit and data.split()[8] != "0.0.0.0":
								for nick in nicks:
									self.send(":{0} KILL {1} :G-lined".format(self.obot, nick))
								self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.obot, data.split()[8], limit))
							elif conns == limit and data.split()[8] != "0.0.0.0":
								for nick in nicks:
									self.omsg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
								
		except Exception:
			et, ev, tb = sys.exc_info()
			e = "{0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
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
					self.ohelp(source, "TRUST", "IP [LIMIT]")
					self.ohelp(source, "RELOAD")
					self.ohelp(source, "UPDATE")
					self.ohelp(source, "QUIT", "[REASON]")
					self.ohelp(source, "VERSION")
				elif cmd == "reload":
					config.read("pyserv.conf")
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
					self.omsg(source, "Done.")
				elif cmd == "update":
					_web = urllib2.urlopen("https://raw.github.com/Pythonz/PyServ/master/version")
					_version = _web.read()
					_web.close()
					if __version__ != _version:
						self.omsg(source, "{0} -> {1}".format(__version__, _version))
						subprocess.Popen("git add .", shell=True).wait()
						subprocess.Popen("git commit -m 'Save'", shell=True).wait()
						subprocess.Popen("git pull", shell=True).wait()
						__updates = 0
						_sql = list()
						for doc in os.listdir("sql/updates"):
							_sql.append(doc)
							__updates += 1
						if __updates > _updates:
							_files = __updates - _updates
							while _files != 0:
								self.omsg(source, " - Insert '{0}'".format(_sql[-_files]))
								subprocess.Popen("mysql -u {0} -p{1} {2} < sql/updates/{3}".format(self.mysql_user, self.mysql_passwd, self.mysql_name, _sql[-_files]), shell=True).wait()
								_files -= 1
						msg = "We are restarting for an update, please be patient. We are back as soon as possible."
						self.send(":%s QUIT :%s" % (self.bot, msg))
						self.send(":%s QUIT :%s" % (self.obot, msg))
						self.con.close()
						sys.exit(2)
					else: self.omsg(source, "No update available.")
				elif cmd == "trust":
					if len(arg) == 0:
						for trust in self.query("select * from trust"):
							self.omsg(source, "IP: {0}          Limit: {1}".format(trust[0], trust[1]))
					elif len(arg) == 1:
						entry = False
						for trust in self.query("select * from trust where address = '{0}'".format(arg[0])):
							entry = True
							self.query("delete from trust where address = '{0}'".format(trust[0]))
						if entry:
							self.omsg(source, "Trust for {0} has been deleted.".format(arg[0]))
							conns = 0
							nicks = list()
							for online in self.query("select nick from online where address = '{0}'".format(arg[0])):
								nicks.append(online[0])
								conns += 1
							if conns > 3 and arg[0] != "0.0.0.0":
								for nick in nicks:
									self.send(":{0} KILL {1} :G-lined".forma(self.obot, nick))
								self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.obot, arg[0], limit))
							elif conns == 3 and arg[0] != "0.0.0.0":
								for nick in nicks:
									self.omsg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
						else:
							self.omsg(source, "Trust for {0} does not exist.".format(arg[0]))
					elif len(arg) == 2:
						entry = False
						for trust in self.query("select * from trust where address = '{0}'".format(arg[0])):
							entry = True
						if entry:
							limit = filter(lambda x: x.isdigit(), arg[1])
							if limit != "":
								self.query("update trust set `limit` = '{0}' where address = '{1}'".format(limit, arg[0]))
								self.omsg(source, "Trust for {0} has been set to {1}.".format(arg[0], limit))
								conns = 0
								nicks = list()
								for online in self.query("select nick from online where address = '{0}'".format(arg[0])):
									nicks.append(online[0])
									conns += 1
								if conns > int(limit) and arg[0] != "0.0.0.0":
									for nick in nicks:
										self.send(":{0} KILL {1} :G-lined".forma(self.obot, nick))
									self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.obot, arg[0], limit))
								elif conns == int(limit) and arg[0] != "0.0.0.0":
									for nick in nicks:
										self.omsg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
							else:
								self.omsg(source, "Invalid limit")
						else:
							limit = filter(lambda x: x.isdigit(), arg[1])
							if limit != "":
								self.query("insert into  trust values ('{1}','{0}')".format(limit, arg[0]))
								self.omsg(source, "Trust for {0} has been set to {1}.".format(arg[0], limit))
								conns = 0
								nicks = list()
								for online in self.query("select nick from online where address = '{0}'".format(arg[0])):
									nicks.append(online[0])
									conns += 1
								if conns > int(limit) and arg[0] != "0.0.0.0":
									for nick in nicks:
										self.send(":{0} KILL {1} :G-lined".forma(self.obot, nick))
									self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.obot, arg[0], limit))
								elif conns == int(limit) and arg[0] != "0.0.0.0":
									for nick in nicks:
										self.omsg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
							else:
								self.omsg(source, "Invalid limit")
					else: self.omsg(source, "TRUST [<address> [<limit>]]")
				elif cmd == "vhost":
					if len(arg) == 1:
						if arg[0].lower() == "list":
							for data in self.query("select user,vhost from vhosts where active = '0'"):
								self.omsg(source, "User: %s\t|\tRequested vHost: %s" % (str(data[0]), str(data[1])))
					elif len(arg) == 2:
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
					else: self.omsg(source, "Syntax: VHOST <list>/<activate>/<reject> [<user>]")
				elif cmd == "global":
					self.omsg("$*", "[%s] " % self.nick(source) + args)
				elif cmd == "feedback":
					if len(args) == 0:
						self.omsg(source, "Following users sent a feedback:")
						for data in self.query("select user from feedback"):
							self.omsg(source, str(data[0]))
						self.omsg(source, "To read a feedback: FEEDBACK <user>")
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
						self.omsg(source, "Syntax: KILL <nick>")
				elif cmd == "quit":
					if len(arg) == 0:
						msg = "services shutdown"
						self.send(":%s QUIT :%s" % (self.bot, msg))
						self.send(":%s QUIT :%s" % (self.obot, msg))
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
		except Exception:
			self.omsg(source, "An error has occured. The Development-Team has been notified about this problem.")
			et, ev, tb = sys.exc_info()
			e = "{0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
			if self.email != "":
				self.mail("bugs@skyice.tk", "From: {0} <{1}>\nTo: PyServ Development <bugs@skyice.tk>\nSubject: Bug on {0}\n{2}".format(self.services_description, self.email, str(e)))
			debug("<<OMSG-ERROR>> "+str(e))

	def message(self, source, text):
		try:
			arg = text.split()
			if text.lower().split()[0] == "help":
				self.help(source, "HELP", "Shows information about all commands that are available to you")
				self.help(source, "AUTH", "Authes you")
				self.help(source, "HELLO", "Creates an account")
				if self.auth(source) != 0:
					self.help(source, "NEWPASS", "Changes your password")
					self.help(source, "VHOST", "Requests a vHost for your Account")
					self.help(source, "REQUEST", "Request for a channel")
					self.help(source, "REMOVE", "Removes a channel")
					self.help(source, "CHANLEV", "Edits your channel records")
					self.help(source, "CHANMODE", "Sets modes for your channel")
					self.help(source, "CHANFLAGS", "Sets flags for your channel")
					self.help(source, "INVITE", "Invites you into a channel")
					self.help(source, "KICK", "Kicks someone from the channel")
					self.help(source, "SYNC", "Syncs your flags on all channels")
					self.help(source, "OWNER", "Sets your owner (+q) flag")
					self.help(source, "DEOWNER", "Removes your owner (+q) flag")
					self.help(source, "PROTECT", "Sets admin (+a) flag to you or someone on the channel")
					self.help(source, "DEPROTECT", "Removes admin (+a) flag from you or someone on the channel")
					self.help(source, "OP", "Sets op (+o) flag to you or someone on the channel")
					self.help(source, "DEOP", "Removes op (+o) flag from you or someone on the channel")
					self.help(source, "VOICE", "Sets voice (+v) flag to you or someone on the channel")
					self.help(source, "DEVOICE", "Removes voice (+v) flag from you or someone on the channel")
					self.help(source, "SETTOPIC", "Sets topic for your channel")
					self.help(source, "WELCOME", "Sets a welcome message for your channel")
					self.help(source, "SETWHOIS", "Sets cool stuff in your whois")
					self.help(source, "FEEDBACK", "Sends a feedback to us")
					self.help(source, "WHOIS", "Shows information about a user")
				self.help(source, "VERSION", "Shows version of services")
			elif arg[0].lower() == "setwhois" and self.auth(source) != 0:
				if len(arg) > 1:
					self.send(":{uid} SWHOIS {target} :{text}".format(uid=self.bot, target=source, text=' '.join(arg[1:])))
					self.msg(source, "Done.")
				else:
					self.send(":{uid} SWHOIS {target} :".format(uid=self.bot, target=source))
					self.msg(source, "Done.")
			elif arg[0].lower() == "invite" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) != 0:
							self.send(":{0} INVITE {1} {2}".format(self.bot, source, arg[1]))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: INVITE <#channel>")
			elif arg[0].lower() == "welcome" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						entry = False
						for data in self.query("select name,welcome from channelinfo where name = '{0}'".format(arg[1])):
							self.msg(source, "[{0}] {1}".format(data[0], data[1]))
							entry = True
						if not entry:
							self.msg(source, "Channel {0} does not exist".format(arg[1]))
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						welcome = _mysql.escape_string(' '.join(arg[2:]))
						if flag == "n" or flag == "q" or flag == "a":
							self.query("update channelinfo set welcome = '{0}' where name = '{1}'".format(welcome, arg[1]))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: WELCOME <#channel> [<text>]")
			elif arg[0].lower() == "sync" and self.auth(source) != 0:
				self.flag(source)
				self.msg(source, "Done.")
			elif arg[0].lower() == "owner" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "q":
							self.mode(arg[1], "+q {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: OWNER <#channel>")
			elif arg[0].lower() == "deowner" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "q":
							self.mode(arg[1], "-q {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: DEOWNER <#channel>")
			elif arg[0].lower() == "protect" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a":
							self.mode(arg[1], "+a {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q":
							self.mode(arg[1], "+{0} {1}".format("a"*len(arg[2:]), ' '.join(arg[2:])))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: PROTECT <#channel> [<nick> [<nick>]]")
			elif arg[0].lower() == "deprotect" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a":
							self.mode(arg[1], "-a {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q":
							self.mode(arg[1], "-{0} {1}".format("a"*len(arg[2:]), ' '.join(arg[2:])))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: DEPROTECT <#channel> [<nick> [<nick>]]")
			elif arg[0].lower() == "op" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a" or flag == "o":
							self.mode(arg[1], "+o {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a" or flag == "o":
							self.mode(arg[1], "+{0} {1}".format("o"*len(arg[2:]), ' '.join(arg[2:])))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: OP <#channel> [<nick> [<nick>]]")
			elif arg[0].lower() == "deop" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a" or flag == "o":
							self.mode(arg[1], "-o {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a" or flag == "o":
							self.mode(arg[1], "-{0} {1}".format("o"*len(arg[2:]), ' '.join(arg[2:])))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: DEOP <#channel> [<nick> [<nick>]]")
			elif arg[0].lower() == "voice" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "v":
							self.mode(arg[1], "+v {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "q" or flag == "a" or flag == "o":
							self.mode(arg[1], "+{0} {1}".format("v"*len(arg[2:]), ' '.join(arg[2:])))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: VOICE <#channel> [<nick> [<nick>]]")
			elif arg[0].lower() == "devoice" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "a" or flag == "o" or flag == "v":
							self.mode(arg[1], "-v {0}".format(source))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 2:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "a" or flag == "o":
							self.mode(arg[1], "-{0} {1}".format("v"*len(arg[2:]), ' '.join(arg[2:])))
							self.msg(source, "Done.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: DEVOICE <#channel> [<nick> [<nick>]]")
			elif arg[0].lower() == "kick" and self.auth(source) != 0:
				if len(arg) == 3:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "a" or flag =="o":
							if arg[2].lower() != "q" and not self.isoper(self.uid(arg[2])):
								self.send(":{0} KICK {1} {2} :{2}".format(self.bot, arg[1], arg[2]))
								self.msg(source, "Done.")
							else: self.msg(source, "Denied.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) > 3:
					if arg[1].startswith("#"):
						flag = self.getflag(source, arg[1])
						if flag == "n" or flag == "a" or flag =="o":
							if arg[2].lower() != "q" and not self.isoper(self.uid(arg[2])):
								self.send(":{0} KICK {1} {2} :{3}".format(self.bot, arg[1], arg[2], ' '.join(arg[3:])))
								self.msg(source, "Done.")
							else: self.msg(source, "Denied.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				else: self.msg(source, "Syntax: KICK <#channel> <user> [,<user>] [reason]")
			elif arg[0].lower() == "newpass" and self.auth(source) != 0:
				if len(arg) == 2:
					self.query("update users set pass = '%s' where name = '%s'" % (self.hash(arg[1]), self.auth(source)))
					self.msg(source, """Your new password is "%s". Remember it!""" % arg[1])
				else:
					self.msg(source, "Syntax: NEWPASS <password>")
			elif arg[0].lower() == "hello":
				if self.auth(source) != 0:
					self.msg(source, "HELLO is not available once you have authed.")
					return 0
				if len(arg) == 3:
					exists = False
					for data in self.query("select name from users where email = '%s' or name = '%s'" % (arg[1], self.nick(source))):
							exists = True
					if not exists:
						if arg[1].find("@") != -1 and arg[1].find(".") != -1 and arg[1].lower() == arg[2].lower():
							self.query("insert into users values ('%s','%s','%s')" % (self.nick(source), self.hash(hash(arg[1])), arg[1]))
							self.msg(source, "The account %s has been created successfully. You can login now with /msg Q auth account password" % self.nick(source))
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
					self.msg(source, "Syntax: HELLO <email> <email>")
			elif text.lower().split()[0] == "auth":
				if self.auth(source) != 0:
					self.msg(source, "AUTH is not available once you have authed.");
					return 0
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
					self.msg(source, "Syntax: AUTH <username> <password>")
			elif text.lower().split()[0] == "vhost" and self.auth(source) != 0:
				if len(text.split()) == 2:
					self.query("delete from vhosts where user = '%s'" % self.auth(source))
					self.query("insert into vhosts values ('%s','%s','0')" % (self.auth(source), text.split()[1]))
					self.msg(source, "Your new vhost\2 %s\2 has been requested" % text.split()[1])
					self.vhost(source)
				else:
					self.msg(source, "Syntax: VHOST <vhost>")
			elif text.lower().split()[0] == "request" and self.auth(source) != 0:
				if len(text.split()) == 2 and text.split()[1].startswith("#"):
					exists = False
					for data in self.query("select channel from channels"):
						if text.lower().split()[1] == str(data[0]).lower():
							exists = True
					if not exists:
						self.query("insert into channelinfo values ('%s', '', '', '', '')" % text.split()[1])
						self.query("insert into channels values ('%s','%s','n')" % (text.split()[1], self.auth(source)))
						self.join(text.split()[1])
						self.smode(text.split()[1], "+q {0}".format(source))
						self.msg(source, "Channel \2%s\2 has been registered for you" % text.split()[1])
					else:
						self.msg(source, "Channel \2%s\2 is already registered" % text.split()[1])
				else:
					self.msg(source, "An error has happened while registering channel \2%s\2 for you, %s." % (text.split()[1], self.auth(source)))
			elif arg[0].lower() == "remove" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) == "n":
							for data in self.query("select name from channelinfo where name = '{0}'".format(arg[1])):
								self.query("delete from channels where channel = '{0}'".format(data[0]))
								self.query("delete from channelinfo where name = '{0}'".format(data[0]))
								self.msg(source, "Channel {0} has been deleted.".format(data[0]))
								self.send(":{0} PART {1} :Channel {1} has been deleted.".format(self.bot, data[0]))
						else: self.msg(source, "No permission")
					else: self.msg(source, "Invalid channel '{0}'".format(arg[1]))
				else: self.msg(source, "Syntax: REMOVE <#channel>")							
			elif arg[0].lower() == "chanlev" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) != "0":
							channel = text.split()[1]
							self.msg(source, "Known users on {0}:".format(channel))
							self.msg(source, "Username               Flag")
							for data in self.query("select user,flag from channels where channel='{0}'".format(channel)):
								self.msg(source, " {0} {1} {2}".format(data[0], " "*int(24-len(data[0])), data[1]))
							self.msg(source, "End of list.")
						else: self.msg(source, "Denied.")
					else: self.msg(source, "Invalid channel")
				elif len(arg) == 4:
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
				else: self.msg(source, "Syntax: CHANLEV <#channel> [<user> [<flag>]]")
			elif arg[0].lower() == "chanmode" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "q" or self.getflag(source, arg[1]) == "a":
							for channel in self.query("select name,modes from channelinfo where name = '{0}'".format(arg[1])):
								self.msg(source, "Current modes for {0}: {1}".format(channel[0], channel[1]))
						else:
							self.msg(source, "No permission")
					else:
						self.msg(source, "Invalid channel '{0}'".format(arg[1]))
				elif len(arg) == 3:
					modes = arg[2]
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "q" or self.getflag(source, arg[1]) == "a":
							for channel in self.query("select name from channelinfo where name = '{0}'".format(arg[1])):
								self.query("update channelinfo set modes = '{0}' where name = '{1}'".format(modes, channel[0]))
								self.mode(channel[0], modes)
								self.msg(source, "New modes for {0}: {1}".format(channel[0], modes))
						else:
							self.msg(source, "No permission")
					else:
						self.msg(source, "Invalid channel '{0}'".format(arg[1]))
				else:
					self.msg(source, "Syntax: CHANMODE <#channel> [<modes>]")
			elif arg[0].lower() == "chanflags" and self.auth(source) != 0:
				if len(arg) == 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "q" or self.getflag(source, arg[1]) == "a":
							for channel in self.query("select name,flags from channelinfo where name = '{0}'".format(arg[1])):
								self.msg(source, "Current flags for {0}: {1}".format(channel[0], channel[1]))
						else:
							self.msg(source, "No permission")
					elif arg[1] == "?":
						mode = list()
						desc = list()
						mode.append("p")
						desc.append("Channel rights Protection")
						mode.append("v")
						desc.append("Autovoice in channel")
						mode.append("t")
						desc.append("Topic save")
						mode.append("m")
						desc.append("Modes enforcement")
						mode.append("w")
						desc.append("Welcome message on join")
						mode.append("l")
						desc.append("used for channel logs")
						listed = 0
						while listed != len(mode):
							self.msg(source, "{0}: {1}".format(mode[listed], desc[listed]))
							listed += 1
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
					self.msg(source, "Syntax: CHANFLAGS <#channel> [<flags>]")
			elif arg[0].lower() == "settopic" and self.auth(source) != 0:
				if len(arg) > 2:
					if arg[1].startswith("#"):
						if self.getflag(source, arg[1]) == "n" or self.getflag(source, arg[1]) == "q" or self.getflag(source, arg[1]) == "a":
							self.query("update channelinfo set topic = '{0}' where name = '{1}'".format(_mysql.escape_string(' '.join(arg[2:])), arg[1]))
							self.send(":{0} TOPIC {1} :{2}".format(self.bot, arg[1], ' '.join(arg[2:])))
							if self.chanflag("l", arg[1]): self.log("Q", "topic", arg[1], ":"+' '.join(arg[2:]))
							self.msg(source, "Done.")
						else: self.msg(source, "No permission")
					else: self.msg(source, "Invalid channel '{0}'".format(arg[1]))
				else: self.msg(source, "Syntax: SETTOPIC <#channel> <topic>")
			elif arg[0].lower() == "feedback" and self.auth(source) != 0:
				if len(arg) > 1:
					entry = False
					for data in self.query("select text from feedback where user = '%s'" % self.auth(source)):
						entry = True
					if not entry:
						self.query("insert into feedback values('"+self.auth(source)+"','"+_mysql.escape_string(' '.join(arg[1:]))+"')")
						self.msg(source, "Feedback added to queue.")
						for op in self.query("select uid from opers"):
							self.omsg(str(op[0]), "New feedback from\2 %s\2" % self.auth(source))
					else:
						self.msg(source, "You already sent a feedback. Please wait until an operator read it.")
				else:
					self.msg(source, "FEEDBACK <text>")
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
							self.msg(source, "Online Nicks  : {0}".format(' '.join(online)))
							self.msg(source, "Email address : {0}".format(user[1]))
							self.msg(source, "Known on following channels:")
							self.msg(source, "Channel              Flag")
							for channel in self.query("select channel,flag from channels where user = '{0}'".format(user[0])):
								self.msg(source, " {0}{1}{2}".format(channel[0], " "*int(20-len(channel[0])), channel[1]))
							self.msg(source, "End of list.")
					else:
						for data in self.query("select uid from online where nick = '{0}'".format(arg[1])):
							for user in self.query("select user from temp_nick where nick = '{0}'".format(data[0])):
								entry = True
								for account in self.query("select email from users where name = '{0}'".format(user[0])):
									self.msg(source, "-Information for account {0}:".format(user[0]))
									online = list()
									for uid in self.query("select nick from temp_nick where user = '{0}'".format(user[0])):
										for online_data in self.query("select nick from online where uid = '{0}'".format(uid[0])):
											online.append(online_data[0])
									self.msg(source, "Online Nicks  : {0}".format(' '.join(online)))
									self.msg(source, "Email address : {0}".format(account[0]))
									self.msg(source, "Known on following channels:")
									self.msg(source, "Channel              Flag")
								for channel in self.query("select channel,flag from channels where user = '{0}'".format(user[0])):
									self.msg(source, " {0}{1}{2}".format(channel[0], " "*int(20-len(channel[0])), channel[1]))
								self.msg(source, "End of list.")
					if not entry:
						self.msg(source, "Can\'t find user {0}".format(arg[1]))
				else:
					self.msg(source, "Syntax: WHOIS <nick>/<#account>")
			elif arg[0].lower() == "version": self.version(self.bot, source)
			else:
				self.msg(source, "Unknown command {0}. Please try HELP for more information.".format(arg[0].upper()))
		except Exception:
			self.msg(source, "An error has occured. The Development-Team has been notified about this problem.")
			et, ev, tb = sys.exc_info()
			e = "{0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
			if self.email != "":
				self.mail("bugs@skyice.tk", "From: {0} <{1}>\nTo: PyServ Development <bugs@skyice.tk>\nSubject: Bug on {0}\n{2}".format(self.services_description, self.email, str(e)))
			debug("<<MSG-ERROR>> "+str(e))

	def uid (self, nick):
		if nick == "Q":
			return self.bot
		if nick == "O":
			return self.obot
		for data in self.query("select uid from online where nick = '{0}'".format(nick)):
			return str(data[0])
		return nick

	def nick (self, source):
		if source == self.bot:
			return "Q"
		if source == self.obot:
			return "O"
		for data in self.query("select nick from online where uid = '%s'" % source):
			return str(data[0])
		return source

	def send(self, text):
		self.con.send(text+"\n")
		debug(">> %s" % text)
	def push(self, target, message):
		self.send(":{uid} PUSH {target} ::{message}".format(uid=self.services_id, target=target, message=message))

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
		if target.startswith("#"):
			if self.chanflag("l", target):
				self.log("Q", "mode", target, mode)

	def omode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.obot, target, mode))
		if target.startswith("#"):
			if self.chanflag("l", target):
				self.log("O", "mode", target, mode)

	def smode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.services_id, target, mode))
		if target.startswith("#"):
			if self.chanflag("l", target):
				self.log("Q", "mode", target, mode)

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
		self.smode(channel, "+r")
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
		try:
			mail = smtplib.SMTP('127.0.0.1', 25)
			mail.sendmail(self.email, ['%s' % receiver], message)
			mail.quit()
		except Exception,e: debug("<<MAIL-ERROR>> "+str(e))

	def log(self, source, msgtype, channel, text=""):
		try:
			if msgtype.lower() == "mode" and len(text.split()) > 1:
				nicks = list()
				for nick in text.split()[1:]:
					nicks.append(self.nick(nick))
				text = "{text} {nicks}".format(text=text.split()[0], nicks=' '.join(nicks))
			sender = self.nick(source)+"!Log@PyServ"
			file = open("logs/"+channel, "ab+")
			lines = file.readlines()
			if len(lines) > 100:
				file.close()
				file = open("logs/"+channel, "wb")
				i = 49
				while i != 0:
					file.write(lines[-i])
					i -= 1
				file.write(sender+" "+msgtype.upper()+" "+channel+" "+text+"\n")
			else:
				file.write(sender+" "+msgtype.upper()+" "+channel+" "+text+"\n")
			file.close()
		except: pass

	def showlog(self, source, channel):
		try:
			file = open("logs/"+channel, "rb")
			self.push(source, "!@ PRIVMSG "+channel+" :*** Log start")
			for line in file.readlines():
				self.push(source, line.rstrip())
			self.push(source, "!@ PRIVMSG "+channel+" :*** Log end")
			file.close()
		except: pass

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
