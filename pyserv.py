#!/usr/bin/env python

import sys
import socket
import os
import configparser
import time
import hashlib
import smtplib
import _mysql
import subprocess
import urllib.request, urllib.error, urllib.parse
import traceback
import _thread
import subprocess
import fnmatch
import ssl

try:
	if not os.access("logs", os.F_OK):
		os.mkdir("logs")
	config = configparser.RawConfigParser()
	config.read("pyserv.conf")
except Exception:
	et, ev, tb = sys.exc_info()
	print(("<<ERROR>> {0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))))

def debug(text):
	if config.get("OTHER", "debug") == "1":
		print((str(text)))

def shell(text):
	subprocess.Popen(text+" >> /dev/null", shell=True).wait()

def perror(text):
	try:
		debug(text)
		file = open("error.log", "ab")
		file.write(text+"\n")
		file.close()
	except: pass

def status():
	sock = socket.socket()
	sock.bind(("0.0.0.0", 5556))
	sock.listen(1024)
	while 1: pass
	sock.close()

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
		self.ipv6 = config.getboolean("OTHER", "ipv6")
		self.ssl = config.getboolean("OTHER", "ssl")
		self.status = config.getboolean("OTHER", "status")
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
			if self.status:
				_thread.start_new_thread(status,())
			if self.ipv6:
				if self.ssl:
					self.con = ssl.wrap_socket(socket.socket(socket.AF_INET6, socket.SOCK_STREAM))
				else:
					self.con = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			else:
				if self.ssl:
					self.con = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
				else:
					self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.con.connect((self.server_address, int(self.server_port)))
			self.send("SERVER %s %s 0 %s :%s" % (self.services_name, self.server_password, self.services_id, self.services_description))
			self.send(":%s BURST" % self.services_id)
			self.send(":%s ENDBURST" % self.services_id)
			_thread.start_new_thread(self.sendcache, (self.con,))
			spamscan = {}
			_connected = False
			while 1:
				recv = self.con.recv(25600)
				if not recv:
					self.reconnect()
					return 0
				for data in recv.splitlines():
					debug("<< %s" % data)
					if data.rstrip() != "":
						if data.split()[1] == "PING":
							self.send(":%s PONG %s %s" % (self.services_id, self.services_id, data.split()[2]))
							self.send(":%s PING %s %s" % (self.services_id, self.services_id, data.split()[2]))
						if data.split()[1] == "ENDBURST" and not _connected:
							self.send(":%s UID %s %s Q %s %s TheQBot 0.0.0.0 %s +Ik :The Q Bot" % (self.services_id, self.bot, time.time(), self.services_name, self.services_name, time.time()))
							_connected = True
							self.send(":%s OPERTYPE Service" % self.bot)
							self.meta(self.bot, "accountname", "Q")
							self.msg("$*", "Services are now back online. Have a nice day :)")
							for channel in self.query("select name,modes,topic from channelinfo"):
								self.join(str(channel["name"]))
								if self.chanflag("m", channel["name"]):
									self.mode(channel["name"], channel["modes"])
								if self.chanflag("t", channel["name"]):
									self.send(":{0} TOPIC {1} :{2}".format(self.bot, channel["name"], channel["topic"]))
									if self.chanflag("l", channel["name"]): self.log("Q", "topic", channel["name"], ":"+channel["topic"])
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
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd, cmd, data.split()[0][1:], ' '.join(data.split()[4:]).replace("'", "\\'")))
											if cmd_auth:
												if self.auth(data.split()[0][1:]):
													if len(data.split()) == 4:
														exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd, cmd, data.split()[0][1:]))
													if len(data.split()) > 4:
														exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd, cmd, data.split()[0][1:], ' '.join(data.split()[4:]).replace("'", "\\'")))
												else: self.msg(data.split()[0][1:], "Unknown command {0}. Please try HELP for more information.".format(cmd.upper()))
										if oper == 1:
											if self.isoper(data.split()[0][1:]):
												if len(data.split()) == 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd, cmd, data.split()[0][1:]))
												if len(data.split()) > 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd, cmd, data.split()[0][1:], ' '.join(data.split()[4:]).replace("'", "\\'")))
											else: self.msg(data.split()[0][1:], "You do not have sufficient privileges to use '{0}'".format(data.split()[3][1:].upper()))
								if not iscmd:
									self.message(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "privmsg", data.split()[2], ' '.join(data.split()[3:]))
							if self.chanexist(data.split()[2]):
								puid = data.split()[0][1:]
								pchan = data.split()[2]
								if self.chanflag("s", pchan):
									messages = 10
									seconds = [6, 5]
									for dump in self.query("select spamscan from channelinfo where name = '%s'" % pchan):
										messages = int(dump["spamscan"].split(":")[0])
										seconds = [int(dump["spamscan"].split(":")[1]) + 1, int(dump["spamscan"].split(":")[1])]
									if (pchan, puid) in spamscan:
										num = spamscan[pchan,puid][0] + 1
										spamscan[pchan,puid] = [num, spamscan[pchan,puid][1]]
										timer = int(time.time()) - spamscan[pchan,puid][1]
										if spamscan[pchan,puid][0] == messages and timer < seconds[0]:
											if self.isoper(puid): self.msg(puid, "WARNING: You are flooding {0}. Please stop that, but I won't kill you because you're an IRC Operator.")
											else: self.kill(puid)
											del spamscan[pchan,puid]
										elif timer > seconds[1]:
											spamscan[pchan,puid] = [1, int(time.time())]
									else:
										spamscan[pchan,puid] = [1, int(time.time())]
						if data.split()[1] == "NOTICE":
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "notice", data.split()[2], ' '.join(data.split()[3:]))
						if data.split()[1] == "NICK":
							self.query("update online set nick = '%s' where uid = '%s'" % (data.split()[2], str(data.split()[0])[1:]))
						if data.split()[1] == "KICK":
							arg = data.split()
							knick = arg[0][1:]
							kchan = arg[2]
							ktarget = arg[3]
							kreason = ' '.join(arg[4:])[1:]
							if ktarget == self.bot:
								self.join(kchan)
							else:
								self.query("delete from chanlist where channel = '{0}' and uid = '{1}'".format(kchan, ktarget))
						if data.split()[1] == "QUIT":
							for qchan in self.query("select * from chanlist where uid = '{0}'".format(data.split()[0][1:])):
								if self.chanflag("l", qchan["channel"]):
									if len(data.split()) == 2:
										self.log(qchan["uid"], "quit", qchan["channel"])
									else:
										self.log(qchan["uid"], "quit", qchan["channel"], ' '.join(data.split()[2:])[1:])
							self.query("delete from chanlist where uid = '{0}'".format(data.split()[0][1:]))
							self.query("delete from temp_nick where nick = '%s'" % str(data.split()[0])[1:])
							self.query("delete from online where uid = '%s'" % str(data.split()[0])[1:])
						if data.split()[1] == "TOPIC":
							if len(data.split()) > 1:
								if self.chanflag("l", data.split()[2]): self.log(data.split()[0][1:], "topic", data.split()[2], ' '.join(data.split()[3:]))
								if self.chanflag("t", data.split()[2]):
									for channel in self.query("select topic from channelinfo where name = '{0}'".format(data.split()[2])):
										self.send(":{0} TOPIC {1} :{2}".format(self.bot, data.split()[2], channel["topic"]))
										if self.chanflag("l", data.split()[2]): self.log("Q", "topic", data.split()[2], ":"+channel["topic"])
						if data.split()[1] == "FMODE":
							if self.chanflag("l", data.split()[2]) and len(data.split()) > 4:
								self.log(data.split()[0][1:], "mode", data.split()[2], ' '.join(data.split()[4:]))
							if self.chanflag("m", data.split()[2]) and len(data.split()) == 5:
								if data.split()[2].startswith("#"):
									for channel in self.query("select name,modes from channelinfo where name = '{0}'".format(data.split()[2])):
										self.mode(channel["name"], channel["modes"])
							if len(data.split()) > 5:
								if self.chanexist(data.split()[2]):
									splitted = data.split()[4]
									if splitted.find("+") != -1:
										splitted = splitted.split("+")[1]
									if splitted.find("-") != -1:
										splitted = splitted.split("-")[0]
									flag = self.getflag(data.split()[0][1:], data.split()[2])
									if flag == "h" or flag == "o" or flag == "a" or flag == "q" or flag == "n":
										if splitted.find("b") != -1:
											self.checkbans(data.split()[2], ' '.join(data.split()[5:]))
											for ban in data.split()[5:]:
												if fnmatch.fnmatch(ban, "*!*@*"):
													entry = False
													for sql in self.query("select ban from banlist where ban = '%s' and channel = '%s'" % (ban, data.split()[2])):
														entry = True
													if not entry:
														self.query("insert into banlist values ('%s','%s')" % (data.split()[2], ban))
														self.msg(data.split()[0][1:], "Done.")
									else: self.mode(data.split()[2], "-{0} {1}".format("b"*len(data.split()[5:]), ' '.join(data.split()[5:])))
									splitted = data.split()[4]
									if splitted.find("-") != -1:
										splitted = splitted.split("-")[1]
										if splitted.find("+") != -1:
											splitted = splitted.split("+")[0]
										flag = self.getflag(data.split()[0][1:], data.split()[2])
										if flag == "h" or flag == "o" or flag == "a" or flag == "q" or flag == "n":
											if splitted.find("b") != -1:
												for ban in data.split()[5:]:
													if fnmatch.fnmatch(ban, "*!*@*"):
														entry = False
														for sql in self.query("select ban from banlist where channel = '%s' and ban = '%s'" % (data.split()[2], ban)):
															entry = True
														if entry:
															self.query("delete from banlist where channel = '%s' and ban = '%s'" % (data.split()[2], ban))
															self.msg(data.split()[0][1:], "Done.")
										else: self.mode(data.split()[2], "+{0} {1}".format("b"*len(data.split()[5:]), ' '.join(data.split()[5:])))
								if self.chanflag("b", data.split()[2]):
									mchan = data.split()[2]
									splitted = data.split()[4]
									musers = data.split()[5:]
									if splitted.find("+") != -1:
										splitted = splitted.split("+")[1]
										if splitted.find("-") != -1:
											splitted = splitted.split("-")[0]
										if splitted.find("v") != -1:
											for user in musers:
												flag = self.getflag(self.uid(user), mchan)
												if flag != "v" and flag != "h" and flag != "o" and flag != "a" and flag != "q" and flag != "n" and self.uid(user) != self.bot:
													self.mode(mchan, "-v "+user)
										if splitted.find("h") != -1:
											for user in musers:
												flag = self.getflag(self.uid(user), mchan)
												if flag != "h" and flag != "o" and flag != "a" and flag != "q" and flag != "n" and self.uid(user) != self.bot:
													self.mode(mchan, "-h "+user)
										if splitted.find("o") != -1:
											for user in musers:
												flag = self.getflag(self.uid(user), mchan)
												if flag != "o" and flag != "a" and flag != "q" and flag != "n" and self.uid(user) != self.bot:
													self.mode(mchan, "-o "+user)
										if splitted.find("a") != -1:
											for user in musers:
												flag = self.getflag(self.uid(user), mchan)
												if flag != "a" and flag != "q" and flag != "n" and self.uid(user) != self.bot:
													self.mode(mchan, "-a "+user)
										if splitted.find("q") != -1:
											for user in musers:
												flag = self.getflag(self.uid(user), mchan)
												if flag != "q" and flag != "n" and self.uid(user) != self.bot:
													self.mode(mchan, "-q "+user)
													
								if self.chanflag("p", data.split()[2]):
									for user in data.split()[5:]:
										for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (data.split()[2], self.auth(user))):
											if str(flag["flag"]) == "n":
												self.mode(data.split()[2], "+q %s" % user)
											elif str(flag["flag"]) == "Y":
												pass
											else:
												self.mode(data.split()[2], "+%s %s" % (str(flag["flag"]), user))
						if data.split()[1] == "FJOIN":
							fjoin_chan = data.split()[2]
							fjoin_nick = data.split()[5][1:]
							if fjoin_nick.find(",") != -1:
								fjoin_nick = fjoin_nick.split(",")[1]
							for pnick in data.split()[5:]:
								if pnick.find(",") != -1:
									pnick = pnick.split(",")[1]
								self.query("insert into chanlist value ('{0}','{1}')".format(pnick, fjoin_chan))
								if self.suspended(fjoin_chan):
									if not self.isoper(pnick):
										self.kick(fjoin_chan, pnick, "Suspended: "+self.suspended(fjoin_chan))
									else:
										self.msg(fjoin_chan, "This channel is suspended: "+self.suspended(fjoin_chan))
							if self.chanexist(fjoin_chan): self.enforcebans(fjoin_chan)
							if self.chanflag("l", fjoin_chan):
								self.showlog(fjoin_nick, fjoin_chan)
								self.log(fjoin_nick, "join", fjoin_chan)
							fjoin_user = self.auth(fjoin_nick)
							hasflag = False
							for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (fjoin_chan, fjoin_user)):
								if str(flag["flag"]) == "n":
									self.mode(fjoin_chan, "+q %s" % fjoin_nick)
									hasflag = True
								elif str(flag["flag"]) == "Y":
									pass
								else:
									self.mode(fjoin_chan, "+%s %s" % (str(flag["flag"]), fjoin_nick))
									hasflag = True
							if not hasflag:
								if self.chanflag("v", fjoin_chan):
									self.mode(fjoin_chan, "+v %s" % fjoin_nick)
							for welcome in self.query("select name,welcome from channelinfo where name = '{0}'".format(fjoin_chan)):
								if self.chanflag("w", fjoin_chan):
									self.msg(fjoin_nick, "[{0}] {1}".format(welcome["name"], welcome["welcome"]))
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
							self.query("delete from online where uid = '%s'" % data.split()[2])
							self.query("delete from online where nick = '%s'" % data.split()[4])
							self.query("insert into online values ('%s','%s','%s','%s','%s')" % (data.split()[2], data.split()[4], data.split()[8], data.split()[5], data.split()[7]))
							conns = 0
							nicks = list()
							for connection in self.query("select nick from online where address = '%s'" % data.split()[8]):
								nicks.append(connection["nick"])
								conns += 1
							limit = 3
							for trust in self.query("select `limit` from trust where address = '%s'" % data.split()[8]):
								limit = int(trust["limit"])
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
			if self.email != "" and ev != "[Errno 111] Connection refused":
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
			cmd = text.lower().split()[0]
			if len(text.split()) > 1:
				arg = text.split()[1:]
				args = ' '.join(text.split()[1:])
			if cmd == "help":
				self.msg(source, "The following commands are available to you.")
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
				self.msg(source, "End of list.")
			elif cmd == "reload" and self.isoper(source):
				config.read("pyserv.conf")
				self.debug = config.get("OTHER", "debug")
				self.email = config.get("OTHER", "email")
				self.regmail = config.get("OTHER", "regmail")
				reload(commands)
				self.msg(source, "Done.")
			elif cmd == "update" and self.isoper(source):
				_web = urllib.request.urlopen("https://raw.github.com/Pythonz/PyServ/master/version")
				_version = _web.read()
				_web.close()
				if open("version", "r").read() != _version:
					
					_updates = len(os.listdir("sql/updates"))
					_hash = hashlib.sha512(open("pyserv.py", "r").read()).hexdigest()
					_modules = list()
					for module in dir(commands):
						if os.access("commands/"+module+".py", os.F_OK):
							_modules.append(module)
					self.msg(source, "{0} -> {1}".format(open("version", "r").read(), _version))
					shell("git add pyserv.conf")
					shell("git commit -m 'Save'")
					shell("git pull")
					_files = os.listdir("sql/updates")
					__updates = len(_files)
					if __updates > _updates:
						while _updates != __updates:
							_updates += 1
							for sql in _files:
								if sql.startswith(str(_updates)+"_"):
									self.msg(source, " - Insert '{0}'".format(sql))
									file = open("sql/updates/"+sql, "r")
									for line in file.readlines():
										self.query(line)
									file.close()
					if _hash != hashlib.sha512(open("pyserv.py", "r").read()).hexdigest():
						self.msg(source, "Done.")
						self.msg(source, "Restart ...")
						msg = "We are restarting for an update, please be patient. We are back as soon as possible."
						self.send(":%s QUIT :%s" % (self.bot, msg))
						self.con.close()
						if os.access("pyserv.pid", os.F_OK): shell("sh pyserv restart")
						else: sys.exit(0)
					else:
						self.msg(source, "Reload ...")
						reload(commands)
						for module in _modules:
							if not os.access("commands/"+module+".py", os.F_OK):
								exec("del commands."+module)
								exec("""del sys.modules["commands.%s"]""" % module)
						self.msg(source, "Done.")
				else: self.msg(source, "No update available.")
			elif cmd == "restart" and self.isoper(source):
				if len(arg) == 0:
					msg = "services restart"
					self.send(":%s QUIT :%s" % (self.bot, msg))
				else:
					self.send(":%s QUIT :%s" % (self.bot, args))
				self.con.close()
				if os.access("pyserv.pid", os.F_OK): shell("sh pyserv restart")
				else: sys.exit(0)
			elif cmd == "quit" and self.isoper(source):
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
			return str(data["uid"])
		return nick

	def nick (self, source):
		if source == self.bot:
			return "Q"
		for data in self.query("select nick from online where uid = '%s'" % source):
			return str(data["nick"])
		return source

	def send(self, text):
		self.con.send(text+"\n")
		debug(">> %s" % text)
	def push(self, target, message):
		self.send(":{uid} PUSH {target} ::{message}".format(uid=self.services_id, target=target, message=message))

	def help(self, target, command, description=""):
		self.msg(target, command.upper()+" "*int(20-len(command))+description)

	def ison(self, user):
		for data in self.query("select * from temp_nick where user = '%s'" % user):
			return True
		return False

	def userflags(self, target):
		user = self.auth(target)
		if user == 0:
			user = target
		for data in self.query("select flags from users where name = '%s'" % user):
			return data["flags"]

	def userflag(self, target, flag):
		user = self.auth(target)
		if self.ison(user):
			for data in self.query("select flags from users where name = '%s'" % user):
				if str(data["flags"]).find(flag) != -1:
					return True
		else:
			if flag == "n":
				return True
		return False

	def msg(self, target, text):
		if self.userflag(target, "n"):
			self.send(":%s NOTICE %s :%s" % (self.bot, target, text))
		else:
			self.send(":%s PRIVMSG %s :%s" % (self.bot, target, text))

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
			return data["user"]
		return 0

	def sid(self, nick):
		nicks = list()
		for data in self.query("select nick from temp_nick where user = '%s'" % nick):
			nicks.append(data["nick"])
		return nicks

	def memo(self, user):
		for data in self.query("select source,message from memo where user = '%s'" % user):
			for source in self.sid(user):
				self.msg(source, "\2[MEMO]\2")
				self.msg(source, "\2FROM:\2 %s" % data["source"])
				self.msg(source, "\2MESSAGE:\2 %s" % data["message"])
			self.query("delete from memo where user = '%s' and source = '%s' and message = '%s'" % (user, data["source"], _mysql.escape_string(data["message"])))

	def chanexist(self, channel):
		for data in self.query("select name from channelinfo where name = '%s'" % channel):
			return True
		return False

	def join(self, channel):
		self.send(":%s JOIN %s" % (self.bot, channel))
		self.mode(channel, "+r")
		self.mode(channel, "+q %s" % self.bot)

	def kill(self, target, reason="You're violating network rules"):
		if target.lower() != "q" and not self.isoper(self.uid(target)):
			self.send(":%s KILL %s :Killed (%s (%s))" % (self.bot, target, self.services_name, reason))

	def vhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
			vhost = str(data["vhost"])
			if str(data["vhost"]).find("@") != -1:
				vident = vhost.split("@")[0]
				vhost = vhost.split("@")[1]
				self.send(":%s CHGIDENT %s %s" % (self.bot, target, vident))
			self.send(":%s CHGHOST %s %s" % (self.bot, target, vhost))
			self.msg(target, "Your vhost\2 %s\2 has been activated" % data["vhost"])

	def flag(self, target):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag,channel from channels where user = '%s'" % str(data["user"])):
				if str(flag["flag"]) == "n":
					self.mode(str(flag["channel"]), "+q %s" % target)
				elif str(flag["flag"]) == "Y":
					pass
				else:
					self.mode(str(flag["channel"]), "+%s %s" % (str(flag["flag"]), target))

	def autojoin(self, target):
		user = self.auth(target)
		if self.ison(user):
			if self.userflag(target, "a"):
				for data in self.query("select channel,flag from channels where user = '%s'" % user):
					channel = data["channel"]
					flag = data["flag"]
					if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h" or flag == "v":
						self.send(":%s SVSJOIN %s %s" % (self.bot, target, channel))

	def getflag(self, target, channel):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (channel, data["user"])):
				return flag["flag"]
		return 0

	def chanflag(self, flag, channel):
		for data in self.query("select flags from channelinfo where name = '{0}'".format(channel)):
			if data["flags"].find(flag) != -1:
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
		if result:
			results = list()
			for data in result.fetch_row(maxrows=0, how=1):
				results.append(data)
			return results

	def mail(self, receiver, message):
		try:
			mail = smtplib.SMTP('127.0.0.1', 25)
			mail.sendmail(self.email, ['%s' % receiver], message)
			mail.quit()
		except Exception as e: debug("<<MAIL-ERROR>> "+str(e))

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

	def kick(self, channel, target, reason="Requested."):
		if self.onchan(channel, target):
			self.send(":{uid} KICK {channel} {target} :{reason}".format(uid=self.bot, target=target, channel=channel, reason=reason))
			self.query("delete from chanlist where channel = '{0}' and uid = '{1}'".format(channel, target))

	def userlist(self, channel):
		uid = list()
		for user in self.query("select uid from chanlist where channel = '%s'" % channel):
			uid.append(user["uid"])
		return uid

	def onchan(self, channel, target):
		uid = self.uid(target)
		for data in self.query("select * from chanlist where channel = '%s' and uid = '%s'" % (channel, uid)):
			return True
		return False

	def gethost(self, target):
		uid = self.uid(target)
		for data in self.query("select host from online where uid = '%s'" % uid):
			return data["host"]
		return 0

	def hostmask(self, target):
		uid = self.uid(target)
		masks = list()
		nick = None
		username = None
		for data in self.query("select nick,username,host from online where uid = '%s'" % uid):
			nick = data["nick"]
			username = data["username"]
			masks.append(data["nick"]+"!"+data["username"]+"@"+data["host"])
		if self.auth(uid) != 0:
			for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(uid)):
				if str(data["vhost"]).find("@") != -1:
					masks.append(nick+"!"+data["vhost"])
				else:
					masks.append(nick+"!"+username+"@"+data["vhost"])
		return masks

	def enforceban(self, channel, target):
		for user in self.userlist(channel):
			for hostmask in self.hostmask(user):
				if fnmatch.fnmatch(hostmask, target):
					self.mode(channel, "+b "+target)
					self.kick(channel, user, "Banned.")

	def enforcebans(self, channel):
		for data in self.query("select ban from banlist where channel = '%s'" % channel):
			for user in self.userlist(channel):
				for hostmask in self.hostmask(user):
					if fnmatch.fnmatch(hostmask, data["ban"]):
						self.mode(channel, "+b "+data["ban"])
						self.kick(channel, user, "Banned.")

	def checkbans(self, channel, bans):
		if self.chanflag("e", channel):
			for ban in bans.split():
				if fnmatch.fnmatch(ban, "*!*@*"):
					for user in self.userlist(channel):
						for hostmask in self.hostmask(user):
							if fnmatch.fnmatch(hostmask, ban):
								self.kick(channel, user, "Banned.")
						for ip in self.getip(user):
							if fnmatch.fnmatch("*!*@"+ip, ban):
								self.kick(channel, user, "Banned.")

	def getip(self, target):
		uid = self.uid(target)
		for data in self.query("select address from online where uid = '%s'" % uid):
			return data["address"]
		return 0

	def gline(self, target, reason=""):
		uid = self.uid(target)
		ip = self.getip(uid)
		for data in self.query("select uid from online where address = '%s'" % self.getip(uid)):
			self.send(":"+self.bot+" KILL "+data["uid"]+" :G-lined")
		self.send(":"+self.bot+" GLINE *@"+ip+" 1800 :"+reason)

	def suspended(self, channel):
		for data in self.query("select reason from suspended where channel = '%s'" % channel):
			return data["reason"]
		return False

	def userhost(self, target):
		uid = self.uid(target)
		for data in self.query("select username,host from online where uid = '%s'" % uid):
			return data["username"]+"@"+data["host"]
		return 0

	def getvhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % target):
			return data["vhost"]
		return "None"

class Command:
	import sys
	import os
	import configparser
	import time
	import hashlib
	import smtplib
	import _mysql
	import traceback
	import fnmatch
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
		self.ipv6 = config.getboolean("OTHER", "ipv6")
		self.ssl = config.getboolean("OTHER", "ssl")
		self.status = config.getboolean("OTHER", "status")
		self.regmail = config.get("OTHER", "regmail")
		self.bot = "%sAAAAAA" % self.services_id

	def onCommand(self, uid, arguments):
		pass

	def query(self, string):
		Smysql = _mysql.connect(host=self.mysql_host, port=self.mysql_port, db=self.mysql_name, user=self.mysql_user, passwd=self.mysql_passwd)
		Smysql.query(str(string))
		result = Smysql.store_result()
		if result:
			results = list()
			for data in result.fetch_row(maxrows=0, how=1):
				results.append(data)
			Smysql.close()
			return results

	def uid (self, nick):
		if nick == "Q":
			return self.bot
		for data in self.query("select uid from online where nick = '{0}'".format(nick)):
			return data["uid"]
		return nick

	def nick (self, source):
		if source == self.bot:
			return "Q"
		for data in self.query("select nick from online where uid = '%s'" % source):
			return data["nick"]
		return source

	def push(self, target, message):
		self.send(":{uid} PUSH {target} ::{message}".format(uid=self.services_id, target=target, message=message))

	def help(self, target, command, description=""):
		self.msg(target, command.upper()+" "*int(20-len(command))+description)

	def ison(self, user):
		for data in self.query("select * from temp_nick where user = '%s'" % user):
			return True
		return False

	def userflags(self, target):
		user = self.auth(target)
		if user == 0:
			user = target
		for data in self.query("select flags from users where name = '%s'" % user):
			return data["flags"]

	def userflag(self, target, flag):
		user = self.auth(target)
		if self.ison(user):
			for data in self.query("select flags from users where name = '%s'" % user):
				if str(data["flags"]).find(flag) != -1:
					return True
		else:
			if flag == "n":
				return True
		return False

	def msg(self, target, text):
		if self.userflag(target, "n"):
			self.send(":%s NOTICE %s :%s" % (self.bot, target, text))
		else:
			self.send(":%s PRIVMSG %s :%s" % (self.bot, target, text))

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
			return data["user"]
		return 0

	def sid(self, nick):
		nicks = list()
		for data in self.query("select nick from temp_nick where user = '%s'" % nick):
			nicks.append(data["nick"])
		return nicks

	def memo(self, user):
		for data in self.query("select source,message from memo where user = '%s'" % user):
			for source in self.sid(user):
				self.msg(source, "\2[MEMO]\2")
				self.msg(source, "\2FROM:\2 %s" % data["source"])
				self.msg(source, "\2MESSAGE:\2 %s" % data["message"])
			self.query("delete from memo where user = '%s' and source = '%s' and message = '%s'" % (user, data["source"], _mysql.escape_string(data["message"])))

	def chanexist(self, channel):
		for data in self.query("select name from channelinfo where name = '%s'" % channel):
			return True
		return False

	def join(self, channel):
		self.send(":%s JOIN %s" % (self.bot, channel))
		self.mode(channel, "+r")
		self.mode(channel, "+q %s" % self.bot)

	def kill(self, target, reason="You're violating network rules"):
		if target.lower() != "q" and not self.isoper(self.uid(target)):
			self.send(":%s KILL %s :Killed (%s (%s))" % (self.bot, target, self.services_name, reason))

	def vhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
			vhost = str(data["vhost"])
			if str(data["vhost"]).find("@") != -1:
				vident = vhost.split("@")[0]
				vhost = vhost.split("@")[1]
				self.send(":%s CHGIDENT %s %s" % (self.bot, target, vident))
			self.send(":%s CHGHOST %s %s" % (self.bot, target, vhost))
			self.msg(target, "Your vhost\2 %s\2 has been activated" % data["vhost"])

	def flag(self, target):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag,channel from channels where user = '%s'" % str(data["user"])):
				if str(flag["flag"]) == "n":
					self.mode(str(flag["channel"]), "+q %s" % target)
				elif str(flag["flag"]) == "Y":
					pass
				else:
					self.mode(str(flag["channel"]), "+%s %s" % (str(flag["flag"]), target))

	def autojoin(self, target):
		user = self.auth(target)
		if self.ison(user):
			if self.userflag(target, "a"):
				for data in self.query("select channel,flag from channels where user = '%s'" % user):
					channel = data["channel"]
					flag = data["flag"]
					if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h" or flag == "v":
						self.send(":%s SVSJOIN %s %s" % (self.bot, target, channel))

	def getflag(self, target, channel):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (channel, data["user"])):
				return flag["flag"]
		return 0

	def chanflag(self, flag, channel):
		for data in self.query("select flags from channelinfo where name = '{0}'".format(channel)):
			if data["flags"].find(flag) != -1:
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
		except Exception as e: debug("<<MAIL-ERROR>> "+str(e))

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
		debug(">> %s" % text)

	def metadata(self, uid, string, content):
		if string == "accountname":
			self.query("delete from temp_nick where nick = '%s' or user = '%s'" % (uid, content))
			self.query("insert into temp_nick values ('%s','%s')" % (uid, content))
			self.msg(uid, "You are now logged in as %s" % content)
			self.vhost(uid)
			self.flag(uid)
			self.memo(content)

	def kick(self, channel, target, reason="Requested."):
		if self.onchan(channel, target):
			self.send(":{uid} KICK {channel} {target} :{reason}".format(uid=self.bot, target=target, channel=channel, reason=reason))
			self.query("delete from chanlist where channel = '{0}' and uid = '{1}'".format(channel, target))

	def userlist(self, channel):
		uid = list()
		for user in self.query("select uid from chanlist where channel = '%s'" % channel):
			uid.append(user["uid"])
		return uid

	def onchan(self, channel, target):
		uid = self.uid(target)
		for data in self.query("select * from chanlist where channel = '%s' and uid = '%s'" % (channel, uid)):
			return True
		return False

	def gethost(self, target):
		uid = self.uid(target)
		for data in self.query("select host from online where uid = '%s'" % uid):
			return data["host"]
		return 0

	def hostmask(self, target):
		uid = self.uid(target)
		masks = list()
		nick = None
		username = None
		for data in self.query("select nick,username,host from online where uid = '%s'" % uid):
			nick = data["nick"]
			username = data["username"]
			masks.append(data["nick"]+"!"+data["username"]+"@"+data["host"])
		if self.auth(uid) != 0:
			for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(uid)):
				if str(data[0]).find("@") != -1:
					masks.append(nick+"!"+data["vhost"])
				else:
					masks.append(nick+"!"+username+"@"+data["vhost"])
		return masks

	def enforceban(self, channel, target):
		for user in self.userlist(channel):
			for hostmask in self.hostmask(user):
				if fnmatch.fnmatch(hostmask, target):
					self.mode(channel, "+b "+target)
					self.kick(channel, user, "Banned.")

	def enforcebans(self, channel):
		for data in self.query("select ban from banlist where channel = '%s'" % channel):
			for user in self.userlist(channel):
				for hostmask in self.hostmask(user):
					if fnmatch.fnmatch(hostmask, data["ban"]):
						self.mode(channel, "+b "+data["ban"])
						self.kick(channel, user, "Banned.")

	def checkbans(self, channel, bans):
		if self.chanflag("e", channel):
			for ban in bans.split():
				if fnmatch.fnmatch(ban, "*!*@*"):
					for user in self.userlist(channel):
						for hostmask in self.hostmask(user):
							if fnmatch.fnmatch(hostmask, ban):
								self.kick(channel, user, "Banned.")
						for ip in self.getip(user):
							if fnmatch.fnmatch("*!*@"+ip, ban):
								self.kick(channel, user, "Banned.")
	def unknown(self, target):
		self.msg(target, "Unknown command "+__name__.split(".")[-1].upper()+". Please try HELP for more information.")

	def getip(self, target):
		uid = self.uid(target)
		for data in self.query("select address from online where uid = '%s'" % uid):
			return data["address"]
		return 0

	def gline(self, target, reason=""):
		uid = self.uid(target)
		ip = self.getip(uid)
		for data in self.query("select uid from online where address = '%s'" % self.getip(uid)):
			self.send(":"+self.bot+" KILL "+data["uid"]+" :G-lined")
		self.send(":"+self.bot+" GLINE *@"+ip+" 1800 :"+reason)

	def suspended(self, channel):
		for data in self.query("select reason from suspended where channel = '%s'" % channel):
			return data["reason"]
		return False

	def userhost(self, target):
		uid = self.uid(target)
		for data in self.query("select username,host from online where uid = '%s'" % uid):
			return data["username"]+"@"+data["host"]
		return 0

	def getvhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % target):
			return data["vhost"]
		return "None"

class error(Exception):
	def __init__(self, value):
		self.value = value
		self.email = config.get("OTHER", "email")
	def __str__(self):
		try:
			mail = smtplib.SMTP('127.0.0.1', 25)
			mail.sendmail(self.email, ['bugs@skyice.tk'], str(self.value))
			mail.quit()
		except: pass
		finally: return repr(self.value)

if __name__ == "__main__":
	try:
		Services().run()
	except Exception as e: print(e)
	except KeyboardInterrupt: print("Aborting ... STRG +C")
