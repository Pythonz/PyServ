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
import thread
import commands

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

def shell(text):
	subprocess.Popen(text+" >> /dev/null", shell=True).wait()

def perror(text):
	try:
		debug(text)
		file = open("error.log", "ab")
		file.write(text+"\n")
		file.close()
	except: pass

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
		self.db = _mysql.connect(host=self.mysql_host, port=self.mysql_port, db=self.mysql_name, user=self.mysql_user, passwd=self.mysql_passwd)

	def run(self):
		try:
			self.query("delete from temp_nick")
			self.query("delete from opers")
			self.query("delete from online")
			self.query("delete from chanlist")
			shell("rm -rf logs/*")
			self.con = socket.socket()
			self.con.connect((self.server_address, int(self.server_port)))
			self.send("SERVER %s %s 0 %s :%s" % (self.services_name, self.server_password, self.services_id, self.services_description))
			self.send(":%s BURST" % self.services_id)
			self.send(":%s ENDBURST" % self.services_id)
			thread.start_new_thread(self.sendcache, (self.con,))
			
			while 1:
				recv = self.con.recv(25600)
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
							self.msg("$*", "Services are now back online. Have a nice day :)")
							for channel in self.query("select name,modes,topic from channelinfo"):
								self.join(str(channel[0]))
								if self.chanflag("m", channel[0]):
									self.mode(channel[0], channel[1])
								if self.chanflag("t", channel[0]):
									self.send(":{0} TOPIC {1} :{2}".format(self.bot, channel[0], channel[2]))
									if self.chanflag("l", channel[0]): self.log("Q", "topic", channel[0], ":"+channel[2])
						if data.split()[1] == "PRIVMSG":
							if data.split()[2] == self.bot:
								iscmd = False
								for cmd in dir(commands):
									if not cmd.startswith("__") and not cmd.endswith("__") and os.access("commands/"+cmd+".py", os.F_OK) and cmd.lower() == data.split()[3][1:].lower():
										iscmd = True
										exec("oper = commands.%s.%s().oper" % (cmd, cmd))
										if oper == 0:
											exec("cmd_auth = commands.%s.%s().nauth" % (cmd, cmd))
											if not cmd_auth:
												if len(data.split()) == 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd, cmd, data.split()[0][1:]))
												if len(data.split()) > 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd, cmd, data.split()[0][1:], ' '.join(data.split()[4:])))
											if cmd_auth:
												if self.auth(data.split()[0][1:]):
													if len(data.split()) == 4:
														exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd, cmd, data.split()[0][1:]))
													if len(data.split()) > 4:
														exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd, cmd, data.split()[0][1:], ' '.join(data.split()[4:])))
												else: self.msg(data.split()[0][1:], "Unknown command {0}. Please try HELP for more information.".format(cmd.upper()))
										if oper == 1:
											if self.isoper(data.split()[0][1:]):
												if len(data.split()) == 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd, cmd, data.split()[0][1:]))
												if len(data.split()) > 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd, cmd, data.split()[0][1:], ' '.join(data.split()[4:])))
											else: self.msg(data.split()[0][1:], "You do not have sufficient privileges to use '{0}'".format(data.split()[3][1:].upper()))
								if not iscmd:
									self.message(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "privmsg", data.split()[2], ' '.join(data.split()[3:]))
						if data.split()[1] == "NOTICE":
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "notice", data.split()[2], ' '.join(data.split()[3:]))
						if data.split()[1] == "NICK":
							self.query("update online set nick = '%s' where uid = '%s'" % (data.split()[2], str(data.split()[0])[1:]))
						if data.split()[1] == "QUIT":
							for qchan in self.query("select * from chanlist where uid = '{0}'".format(data.split()[0][1:])):
								if self.chanflag("l", qchan[1]):
									if len(data.split()) == 2:
										self.log(qchan[0], "quit", qchan[1])
									else:
										self.log(qchan[0], "quit", qchan[1], ' '.join(data.split()[2:])[1:])
							self.query("delete from chanlist where uid = '{0}'".format(data.split()[0][1:]))
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
							if self.chanflag("l", data.split()[2]) and len(data.split()) > 4:
								self.log(data.split()[0][1:], "mode", data.split()[2], ' '.join(data.split()[4:]))
							if self.chanflag("m", data.split()[2]) and len(data.split()) == 5:
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
							if fjoin_nick.find(",") != -1:
								fjoin_nick = fjoin_nick.split(",")[1]
							self.query("insert into chanlist value ('{0}','{1}')".format(fjoin_nick, fjoin_chan))
							if self.chanflag("l", fjoin_chan):
								if data.split()[5].startswith(","):
									self.showlog(fjoin_nick, fjoin_chan)
									self.log(fjoin_nick, "join", fjoin_chan)
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
						if data.split()[1] == "PART":
							pnick = data.split()[0][1:]
							pchan = data.split()[2]
							self.query("delete from chanlist where uid = '{0}' and channel = '{1}'".format(pnick, pchan))
							if self.chanflag("l", pchan):
								if len(data.split()) == 3:
									self.log(pnick, "part", pchan)
								else:
									self.log(pnick, "part", pchan, ' '.join(data.split()[3:])[1:])
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
							self.query("insert into online values ('%s','%s','%s','%s')" % (data.split()[2], data.split()[4], data.split()[8], data.split()[6]))
							conns = 0
							nicks = list()
							for connection in self.query("select nick from online where address = '%s'" % data.split()[8]):
								nicks.append(connection[0])
								conns += 1
							limit = 3
							for trust in self.query("select `limit` from trust where address = '%s'" % data.split()[8]):
								limit = int(trust[0])
								if data.split()[7].startswith("~"):
									for nick in nicks:
										self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
									self.send(":{0} GLINE *@{1} 1800 :You ignored the trust rules. Run an identd before you connect again.".format(self.bot, data.split()[8]))
							if conns > limit and data.split()[8] != "0.0.0.0":
								for nick in nicks:
									self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
								self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.bot, data.split()[8], limit))
							elif conns == limit and data.split()[8] != "0.0.0.0":
								for nick in nicks:
									self.msg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")

		except Exception:
			et, ev, tb = sys.exc_info()
			e = "{0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
			if self.email != "":
				self.mail("bugs@skyice.tk", "From: {0} <{1}>\nTo: PyServ Development <bugs@skyice.tk>\nSubject: Bug on {0}\n{2}".format(self.services_description, self.email, str(e)))
			debug("<<ERROR>> " + str(e))

	def reconnect(self):
		try:
			self.con.close()
		except: pass
		self.run()

	def sendcache(self, sock):
		try:
			file = open("commands/cache.txt", "w")
			file.write("")
			file.close()
			file = open("commands/cache.txt", "r")
			while 1:
				for line in file.readlines():
					sock.send(line.rstrip()+"\n")
			file.close()
		except: pass
			
	def metadata(self, uid, string, content):
		if string == "accountname":
			self.query("delete from temp_nick where nick = '%s'" % uid)
			self.query("insert into temp_nick values ('%s','%s')" % (uid, content))
			self.msg(uid, "You are now logged in as %s" % content)
			self.vhost(uid)
			self.flag(uid)
			self.memo(content)

	def message(self, source, text):
		try:
			arg = text.split()
			if text.lower().split()[0] == "help":
				self.help(source, "HELP", "Shows information about all commands that are available to you")
				for command in dir(commands):
					if not command.startswith("__") and not command.endswith("__") and not command == "commands" and os.access("commands/"+command+".py", os.F_OK):
						exec("cmd_auth = commands.%s.%s().nauth" % (command, command))
						exec("cmd_oper = commands.%s.%s().oper" % (command, command))
						exec("cmd_help = commands.%s.%s().help" % (command, command))
						if not cmd_auth and not cmd_oper:
							self.help(source, command, cmd_help)
						if cmd_auth and not cmd_oper and self.auth(source):
							self.help(source, command, cmd_help)
						if cmd_oper and self.isoper(source):
							self.help(source, command, cmd_help+" \2(oper only)\2")
				if self.isoper(source):
					self.help(source, "RELOAD", "Reloads the config \2(oper only)\2")
					self.help(source, "UPDATE", "Updates the services \2(oper only)\2")
					self.help(source, "RESTART", "Restarts the services \2(oper only)\2")
					self.help(source, "QUIT", "Shutdowns the services \2(oper only)\2")
			if self.isoper(source):
				cmd = text.lower().split()[0]
				arg = text.split()[1:]
				args = ' '.join(text.split()[1:])
				if cmd == "reload":
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
					self.msg(source, "Done.")
				elif cmd == "update":
					_web = urllib2.urlopen("https://raw.github.com/Pythonz/PyServ/master/version")
					_version = _web.read()
					_web.close()
					if __version__ != _version:
						self.msg(source, "{0} -> {1}".format(__version__, _version))
						shell("git add pyserv.conf")
						shell("git commit -m 'Save'")
						shell("git pull")
						__updates = 0
						_sql = list()
						for doc in os.listdir("sql/updates"):
							_sql.append(doc)
							__updates += 1
						if __updates > _updates:
							_files = __updates - _updates
							while _files != 0:
								self.msg(source, " - insert '{0}'".format(_sql[-_files]))
								file = open("sql/updates/{0}".format(_sql[-_files]))
								for line in file.readlines():
									self.query(line)
								file.close()
								_files -= 1
							self.msg(source, "Done.")
						msg = "We are restarting for an update, please be patient. We are back as soon as possible."
						self.send(":%s QUIT :%s" % (self.bot, msg))
						self.con.close()
						if os.access("pyserv.pid", os.F_OK): shell("sh pyserv restart")
						else: sys.exit(0)
				elif cmd == "restart":
					if len(arg) == 0:
						msg = "services restart"
						self.send(":%s QUIT :%s" % (self.bot, msg))
					else:
						self.send(":%s QUIT :%s" % (self.bot, args))
					self.con.close()
					if os.access("pyserv.pid", os.F_OK): shell("sh pyserv restart")
					else: sys.exit(0)
				elif cmd == "quit":
					if os.access("pyserv.pid", os.F_OK):
						if len(arg) == 0:
							msg = "services shutdown"
							self.send(":%s QUIT :%s" % (self.bot, msg))
						else:
							self.send(":%s QUIT :%s" % (self.bot, args))
						self.con.close()
						shell("sh pyserv stop")
					else: self.msg(source, "You are running in debug mode, only restart is possible!")
				else:
					self.msg(source, "Unknown command {0}. Use HELP for more information".format(cmd.upper()))
			else:
				self.msg(source, "Unknown command {0}. Please try HELP for more information.".format(text.split()[0].upper()))
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
		for data in self.query("select uid from online where nick = '{0}'".format(nick)):
			return str(data[0])
		return nick

	def nick (self, source):
		if source == self.bot:
			return "Q"
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

	def msg(self, target, text):
		self.send(":%s NOTICE %s :%s" % (self.bot, target, text))

	def mode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.bot, target, mode))
		if target.startswith("#"):
			if self.chanflag("l", target):
				self.log("Q", "mode", target, mode)

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

	def sid(self, nick):
		for data in self.query("select nick from temp_nick where user = '%s'" % nick):
			return str(data[0])
		return 0

	def memo(self, user):
		source = self.sid(user)
		if source != 0:
			for data in self.query("select source,message from memo where user = '%s'" % user):
				self.msg(source, "[MEMO]")
				self.msg(source, "FROM: %s" % data[0])
				self.msg(source, "MESSAGE: %s" % data[1])
				self.query("delete from memo where user = '%s' and source = '%s' and message = '%s'" % (user, data[0], _mysql.escape_string(data[1])))

	def chanexist(self, channel):
		for data in self.query("select name from channelinfo where name = '%s'" % channel):
			return True
		return False

	def join(self, channel):
		self.send(":%s JOIN %s" % (self.bot, channel))
		self.smode(channel, "+r")
		self.smode(channel, "+q %s" % self.bot)

	def kill(self, target, reason):
		if target.lower() != "o" and target.lower() != "q":
			self.send(":%s KILL %s :Killed (%s (%s))" % (self.bot, target, self.services_name, reason))

	def vhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
			self.send(":%s CHGHOST %s %s" % (self.bot, target, str(data[0])))
			self.msg(target, "Your vhost\2 %s\2 has been activated" % str(data[0]))

	def version(self, source):
		self.msg(source, "PyServ v%s" % __version__)
		self.msg(source, "Uptime: %s" % (self.convert_timestamp(time.time() - _started)))
		self.msg(source, "Running on: %s %s %s" % (os.uname()[0], os.uname()[2], os.uname()[-1]))
		self.msg(source, "Developed by Pythonz (https://github.com/Pythonz). Suggestions to pythonz@skyice.tk.")

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
				if line.split()[1] != "PART" and line.split()[1] != "JOIN" and line.split()[1] != "QUIT":
					self.push(source, line.rstrip())
				else:
					self.push(source, "*!@ PRIVMSG "+channel+" :"+line.rstrip())
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

class Command:
	import sys
	import os
	import ConfigParser
	import time
	import hashlib
	import smtplib
	import _mysql
	import traceback
	help = "unknown"
	oper = 0
	nauth = 0
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

	def onCommand(self, uid, arguments):
		pass

	def query(self, string):
		Smysql = _mysql.connect(host=self.mysql_host, port=self.mysql_port, db=self.mysql_name, user=self.mysql_user, passwd=self.mysql_passwd)
		Smysql.query(str(string))
		result = Smysql.store_result()
		try:
			return result.fetch_row(maxrows=0)
		except:
			pass
		finally:
			Smysql.close()
	def uid (self, nick):
		if nick == "Q":
			return self.bot
		for data in self.query("select uid from online where nick = '{0}'".format(nick)):
			return str(data[0])
		return nick

	def nick (self, source):
		if source == self.bot:
			return "Q"
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

	def msg(self, target, text):
		self.send(":%s NOTICE %s :%s" % (self.bot, target, text))

	def mode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.bot, target, mode))
		if target.startswith("#"):
			if self.chanflag("l", target):
				self.log("Q", "mode", target, mode)

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

	def sid(self, nick):
		for data in self.query("select nick from temp_nick where user = '%s'" % nick):
			return str(data[0])
		return 0

	def memo(self, user):
		source = self.sid(user)
		if source != 0:
			for data in self.query("select source,message from memo where user = '%s'" % user):
				self.msg(source, "[MEMO]")
				self.msg(source, "FROM: %s" % data[0])
				self.msg(source, "MESSAGE: %s" % data[1])
				self.query("delete from memo where user = '%s' and source = '%s' and message = '%s'" % (user, data[0], _mysql.escape_string(data[1])))

	def chanexist(self, channel):
		for data in self.query("select name from channelinfo where name = '%s'" % channel):
			return True
		return False

	def join(self, channel):
		self.send(":%s JOIN %s" % (self.bot, channel))
		self.smode(channel, "+r")
		self.smode(channel, "+q %s" % self.bot)

	def kill(self, target, reason):
		if target.lower() != "o" and target.lower() != "q":
			self.send(":%s KILL %s :Killed (%s (%s))" % (self.bot, target, self.services_name, reason))

	def vhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
			self.send(":%s CHGHOST %s %s" % (self.bot, target, str(data[0])))
			self.msg(target, "Your vhost\2 %s\2 has been activated" % str(data[0]))

	def version(self, source):
		self.msg(source, "PyServ v%s" % __version__)
		self.msg(source, "Uptime: %s" % (self.convert_timestamp(time.time() - _started)))
		self.msg(source, "Running on: %s %s %s" % (os.uname()[0], os.uname()[2], os.uname()[-1]))
		self.msg(source, "Developed by Pythonz (https://github.com/Pythonz). Suggestions to pythonz@skyice.tk.")

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
				if line.split()[1] != "PART" and line.split()[1] != "JOIN" and line.split()[1] != "QUIT":
					self.push(source, line.rstrip())
				else:
					self.push(source, "*!@ PRIVMSG "+channel+" :"+line.rstrip())
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

	def send(self, text):
		file = open("commands/cache.txt", "a")
		file.write("{0}\n".format(str(text)))
		file.close()

	def metadata(self, uid, string, content):
		if string == "accountname":
			self.query("delete from temp_nick where nick = '%s' or user = '%s'" % (uid, content))
			self.query("insert into temp_nick values ('%s','%s')" % (uid, content))
			self.msg(uid, "You are now logged in as %s" % content)
			self.vhost(uid)
			self.flag(uid)
			self.memo(content)

	def unknown(self, target):
		self.msg(target, "Unknown command "+__name__.split(".")[-1].upper()+". Please try HELP for more information.")
		

if __name__ == "__main__":
	try:
		Services().run()
	except Exception,e: print(e)
	except KeyboardInterrupt: print("Aborting ... STRG +C")
