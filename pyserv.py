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
import fnmatch
import ssl
import modules
import __builtin__

def red(string):
	return("\033[91m" + string + "\033[0m")

def blue(string):
	return("\033[94m" + string + "\033[0m")

def green(string):
	return("\033[92m" + string + "\033[0m")

try:
	if not os.access("logs", os.F_OK):
		os.mkdir("logs")
	config = ConfigParser.RawConfigParser()
	if len(sys.argv) == 1:
		config.read("config.cfg")
	else:
		config.read(sys.argv[1])
except Exception:
	et, ev, tb = sys.exc_info()
	print(red("*") + " <<ERROR>> {0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb)))

def debug(text):
	if config.get("OTHER", "debug") == "1":
		print(str(text))

def shell(text):
	subprocess.Popen(text+" >> /dev/null", shell=True).wait()

def perror(text):
	try:
		debug(red("*") + " " + text)
		file = open("error.log", "ab")
		file.write(text+"\n")
		file.close()
	except: pass

def status():
	try:
		sock = socket.socket()
		sock.bind((config.get("SERVICES", "address"), 5556))
		sock.listen(1024)
		while 1:
			time.sleep(1)
		sock.close()
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
		self.ipv6 = config.getboolean("OTHER", "ipv6")
		self.ssl = config.getboolean("OTHER", "ssl")
		self.status = config.getboolean("FAILOVER", "active")
		self.regmail = config.get("OTHER", "regmail")
		self.bot = "%sAAAAAA" % self.services_id
		self.bot_nick = config.get("BOT", "nick").split()[0]
		self.bot_user = config.get("BOT", "user").split()[0]
		self.bot_real = config.get("BOT", "real")
		self.db = _mysql.connect(host=self.mysql_host, port=self.mysql_port, db=self.mysql_name, user=self.mysql_user, passwd=self.mysql_passwd)

	def run(self):
		try:
			self.query("truncate temp_nick")
			self.query("truncate opers")
			self.query("truncate online")
			self.query("truncate chanlist")
			shell("rm -rf logs/*")
			
			if self.status:
				thread.start_new_thread(status,())
				
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
			__builtin__.con = self.con
			spamscan = {}
			_connected = False
			
			while 1:
				recv = self.con.recv(25600)
				
				if not recv:
					return 1
					
				for data in recv.splitlines():
					debug(green("*") + " " + data)
					
					if data.rstrip() != "":
						if data.split()[1] == "PING":
							self.send(":%s PONG %s %s" % (self.services_id, self.services_id, data.split()[2]))
							self.send(":%s PING %s %s" % (self.services_id, self.services_id, data.split()[2]))
						elif data.split()[1] == "ENDBURST" and not _connected:
							self.send(":%s UID %s %s %s %s %s %s 0.0.0.0 %s +Ik :%s" % (self.services_id, self.bot, time.time(), self.bot_nick, self.services_name, self.services_name, self.bot_user, time.time(), self.bot_real))
							_connected = True
							self.send(":%s OPERTYPE Service" % self.bot)
							self.meta(self.bot, "accountname", self.bot_nick)
							self.msg("$*", "Services are now back online. Have a nice day :)")
							
							for channel in self.query("select name,modes,topic from channelinfo"):
								self.join(str(channel["name"]))
								
								if self.chanflag("m", channel["name"]):
									self.mode(channel["name"], channel["modes"])
									
								if self.chanflag("t", channel["name"]):
									self.send(":{0} TOPIC {1} :{2}".format(self.bot, channel["name"], channel["topic"]))
									
									if self.chanflag("l", channel["name"]):
										self.log(self.bot_nick, "topic", channel["name"], ":"+channel["topic"])
						elif data.split()[1] == "PRIVMSG":
							if data.split()[2] == self.bot:
								iscmd = False
								cmd = data.split()[3][1:]
								
								if os.access("commands/"+cmd.lower()+".py", os.F_OK):
									iscmd = True
									exec("oper = commands.%s.%s().oper" % (cmd.lower(), cmd.lower()))
									
									if oper == 0:
										exec("cmd_auth = commands.%s.%s().nauth" % (cmd.lower(), cmd.lower()))
										
										if not cmd_auth:
											if len(data.split()) == 4:
												exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd.lower(), cmd.lower(), data.split()[0][1:]))
											elif len(data.split()) > 4:
												exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd.lower(), cmd.lower(), data.split()[0][1:], ' '.join(data.split()[4:]).replace("'", "\\'")))
										elif cmd_auth:
											if self.auth(data.split()[0][1:]):
												if len(data.split()) == 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd.lower(), cmd.lower(), data.split()[0][1:]))
												elif len(data.split()) > 4:
													exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd.lower(), cmd.lower(), data.split()[0][1:], ' '.join(data.split()[4:]).replace("'", "\\'")))
											else:
												self.msg(data.split()[0][1:], "Unknown command {0}. Please try HELP for more information.".format(cmd.upper()))
									elif oper == 1:
										if self.isoper(data.split()[0][1:]):
											if len(data.split()) == 4:
												exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', ''))" % (cmd.lower(), cmd.lower(), data.split()[0][1:]))
											if len(data.split()) > 4:
												exec("thread.start_new_thread(commands.%s.%s().onCommand,('%s', '%s'))" % (cmd.lower(), cmd.lower(), data.split()[0][1:], ' '.join(data.split()[4:]).replace("'", "\\'")))
										else:
											self.msg(data.split()[0][1:], "You do not have sufficient privileges to use '{0}'".format(data.split()[3][1:].upper()))
											
								if not iscmd:
									self.message(data.split()[0][1:], ' '.join(data.split()[3:])[1:])
									
							if data.split()[2].startswith("#") and self.chanflag("f", data.split()[2]) and self.chanexist(data.split()[2]):
								if data.split()[3][1:].startswith(self.fantasy(data.split()[2])):
									iscmd = False
									fuid = data.split()[0][1:]
									cmd = self.fantasy(data.split()[2])
									
									if len(data.split()[3]) > int(1+len(self.fantasy(data.split()[2]))):
										fchan = data.split()[2]
										cmd = data.split()[3][int(1+len(self.fantasy(fchan))):]
										
										if len(data.split()) > 4:
											args = ' '.join(data.split()[4:]).replace("'", "\\'")
											
										if os.access("commands/"+cmd.lower()+".py", os.F_OK):
											iscmd = True
											exec("oper = commands.%s.%s().oper" % (cmd.lower(), cmd.lower()))
											
											if oper == 0:
												exec("cmd_auth = commands.%s.%s().nauth" % (cmd.lower(), cmd.lower()))
												
												if not cmd_auth:
													if len(data.split()) == 4:
														exec("thread.start_new_thread(commands.%s.%s().onFantasy,('%s', '%s', ''))" % (cmd.lower(), cmd.lower(), fuid, fchan))
													elif len(data.split()) > 4:
														exec("thread.start_new_thread(commands.%s.%s().onFantasy,('%s', '%s', '%s'))" % (cmd.lower(), cmd.lower(), fuid, fchan, args))
												elif cmd_auth:
													if self.auth(fuid):
														if len(data.split()) == 4:
															exec("thread.start_new_thread(commands.%s.%s().onFantasy,('%s', '%s', ''))" % (cmd.lower(), cmd.lower(), fuid, fchan))
														elif len(data.split()) > 4:
															exec("thread.start_new_thread(commands.%s.%s().onFantasy,('%s', '%s', '%s'))" % (cmd.lower(), cmd.lower(), fuid, fchan, args))
													else:
														self.msg(fuid, "Unknown command {0}. Please try HELP for more information.".format(cmd.upper()))
											elif oper == 1:
												if self.isoper(fuid):
													if len(data.split()) == 4:
														exec("thread.start_new_thread(commands.%s.%s().onFantasy,('%s', '%s', ''))" % (cmd.lower(), cmd.lower(), fuid, fchan))
													elif len(data.split()) > 4:
														exec("thread.start_new_thread(commands.%s.%s().onFantasy,('%s', '%s', '%s'))" % (cmd.lower(), cmd.lower(), fuid, fchan, args))
												else:
													self.msg(fuid, "You do not have sufficient privileges to use '{0}'".format(cmd.upper()))
													
									if not iscmd:
										if len(data.split()) == 4:
											self.message(fuid, cmd)
										elif len(data.split()) > 4:
											self.message(fuid, cmd + " " + args)
											
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "privmsg", data.split()[2], ' '.join(data.split()[3:]))
								
							if self.chanexist(data.split()[2]):
								puid = data.split()[0][1:]
								pchan = data.split()[2]
								
								if self.chanflag("s", pchan):
									messages = 10
									seconds = [6, 5]
									
									for dump in self.query("select spamscan from channelinfo where name = '%s'" % _mysql.escape_string(pchan)):
										messages = int(dump["spamscan"].split(":")[0])
										seconds = [int(dump["spamscan"].split(":")[1]) + 1, int(dump["spamscan"].split(":")[1])]
										
									if spamscan.has_key((pchan, puid)):
										num = spamscan[pchan,puid][0] + 1
										spamscan[pchan,puid] = [num, spamscan[pchan,puid][1]]
										timer = int(time.time()) - spamscan[pchan,puid][1]
										
										if spamscan[pchan,puid][0] == messages and timer < seconds[0]:
											if self.isoper(puid):
												self.msg(puid, "WARNING: You are flooding {0}. Please stop that, but I won't kill you because you're an IRC Operator.".format(pchan))
											else:
												self.kill(puid)
												
											del spamscan[pchan,puid]
										elif timer > seconds[1]:
											spamscan[pchan,puid] = [1, int(time.time())]
									else:
										spamscan[pchan,puid] = [1, int(time.time())]
						elif data.split()[1] == "NOTICE":
							if data.split()[2].startswith("#") and self.chanflag("l", data.split()[2]):
								self.log(data.split()[0][1:], "notice", data.split()[2], ' '.join(data.split()[3:]))
						elif data.split()[1] == "NICK":
							self.query("update online set nick = '%s' where uid = '%s'" % (_mysql.escape_string(data.split()[2]), str(data.split()[0])[1:]))
						elif data.split()[1] == "KICK":
							arg = data.split()
							knick = arg[0][1:]
							kchan = arg[2]
							ktarget = self.uid(arg[3])
							kreason = ' '.join(arg[4:])[1:]
							
							if ktarget == self.bot:
								self.join(kchan)
							else:
								self.query("delete from chanlist where channel = '{0}' and uid = '{1}'".format(_mysql.escape_string(kchan), ktarget))
						elif data.split()[1] == "QUIT":
							for qchan in self.query("select * from chanlist where uid = '{0}'".format(data.split()[0][1:])):
								if self.chanflag("l", qchan["channel"]):
									if len(data.split()) == 2:
										self.log(qchan["uid"], "quit", qchan["channel"])
									else:
										self.log(qchan["uid"], "quit", qchan["channel"], ' '.join(data.split()[2:])[1:])
										
							self.query("delete from chanlist where uid = '{0}'".format(data.split()[0][1:]))
							self.query("delete from temp_nick where nick = '%s'" % _mysql.escape_string(str(data.split()[0])[1:]))
							self.query("delete from gateway where uid = '%s'" % str(data.split()[0])[1:])
							self.query("delete from online where uid = '%s'" % str(data.split()[0])[1:])
						elif data.split()[1] == "TOPIC":
							if len(data.split()) > 1:
								if self.chanflag("l", data.split()[2]):
									self.log(data.split()[0][1:], "topic", data.split()[2], ' '.join(data.split()[3:]))
									
								if self.chanflag("t", data.split()[2]):
									for channel in self.query("select topic from channelinfo where name = '{0}'".format(_mysql.escape_string(data.split()[2]))):
										self.send(":{0} TOPIC {1} :{2}".format(self.bot, data.split()[2], channel["topic"]))
										
										if self.chanflag("l", data.split()[2]):
											self.log(self.bot_nick, "topic", data.split()[2], ":"+channel["topic"])
						elif data.split()[1] == "FMODE":
							if self.chanflag("l", data.split()[2]) and len(data.split()) > 4:
								self.log(data.split()[0][1:], "mode", data.split()[2], ' '.join(data.split()[4:]))
								
							if self.chanflag("m", data.split()[2]) and len(data.split()) == 5:
								if data.split()[2].startswith("#"):
									for channel in self.query("select name,modes from channelinfo where name = '{0}'".format(_mysql.escape_string(data.split()[2]))):
										self.mode(channel["name"], channel["modes"])
										
							if len(data.split()) > 5:
								if self.chanexist(data.split()[2]):
									splitted = data.split()[4]
									
									if splitted.find("+") != -1:
										splitted = splitted.split("+")[1]
										
									if splitted.find("-") != -1:
										splitted = splitted.split("-")[0]
										
									flag = self.getflag(data.split()[0][1:], data.split()[2])
									
									if flag == "h" or flag == "o" or flag == "a" or flag == self.bot_nick or flag == "n":
										if splitted.find("b") != -1:
											self.checkbans(data.split()[2], ' '.join(data.split()[5:]))
											
											for ban in data.split()[5:]:
												if fnmatch.fnmatch(ban, "*!*@*"):
													entry = False
													
													for sql in self.query("select ban from banlist where ban = '%s' and channel = '%s'" % (_mysql.escape_string(ban), _mysql.escape_string(data.split()[2]))):
														entry = True
														
													if not entry and ban != "*!*@*":
														self.query("insert into banlist (`channel`, `ban`) values ('%s','%s')" % (_mysql.escape_string(data.split()[2]), _mysql.escape_string(ban)))
														self.msg(data.split()[0][1:], "Done.")
													elif ban == "*!*@*":
														self.msg(data.split()[2], "ACTION is angry about %s, because he tried to set a *!*@* ban." % self.nick(data.split()[0][1:]), True)
									else:
										self.mode(data.split()[2], "-{0} {1}".format("b"*len(data.split()[5:]), ' '.join(data.split()[5:])))
										
									splitted = data.split()[4]
									
									if splitted.find("-") != -1:
										splitted = splitted.split("-")[1]
										
										if splitted.find("+") != -1:
											splitted = splitted.split("+")[0]
											
										flag = self.getflag(data.split()[0][1:], data.split()[2])
										
										if flag == "h" or flag == "o" or flag == "a" or flag == self.bot_nick or flag == "n":
											if splitted.find("b") != -1:
												for ban in data.split()[5:]:
													if fnmatch.fnmatch(ban, "*!*@*"):
														entry = False
														
														for sql in self.query("select ban from banlist where channel = '%s' and ban = '%s'" % (_mysql.escape_string(data.split()[2]), _mysql.escape_string(ban))):
															entry = True
															
														if entry:
															self.query("delete from banlist where channel = '%s' and ban = '%s'" % (_mysql.escape_string(data.split()[2]), _mysql.escape_string(ban)))
															self.msg(data.split()[0][1:], "Done.")
										else:
											self.mode(data.split()[2], "+{0} {1}".format("b"*len(data.split()[5:]), ' '.join(data.split()[5:])))
											
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
												
												if not self.chanflag("v", mchan) and flag != "v" and flag != "h" and flag != "o" and flag != "a" and flag != "q" and flag != "n" and self.uid(user) != self.bot:
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
												
												if flag != "a" and flag != self.bot_nick and flag != "n" and self.uid(user) != self.bot:
													self.mode(mchan, "-a "+user)
													
												if flag != "o":
													self.mode(mchan, "-o "+user)
													
										if splitted.find(self.bot_nick) != -1:
											for user in musers:
												flag = self.getflag(self.uid(user), mchan)
												
												if flag != "q" and flag != "n" and self.uid(user) != self.bot:
													self.mode(mchan, "-q "+user)
													
												if flag != "o":
													self.mode(mchan, "-o "+user)
													
								if self.chanflag("p", data.split()[2]):
									for user in data.split()[5:]:
										fm_chan = data.split()[2]
										
										for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (_mysql.escape_string(data.split()[2]), self.auth(user))):
											if flag["flag"] == "n" or flag["flag"] == "q":
												self.mode(fm_chan, "+qo {0} {0}".format(user))
											elif flag["flag"] == "a":
												self.mode(fm_chan, "+ao {0} {0}".format(user))
											elif flag["flag"] == "o":
												self.mode(fm_chan, "+o {0}".format(user))
											elif flag["flag"] == "h":
												self.mode(fm_chan, "+h {0}".format(user))
											elif flag["flag"] == "v":
												self.mode(fm_chan, "+v {0}".format(user))
											elif flag["flag"] == "b":
												self.kick(fm_chan, user, "Banned.")
						elif data.split()[1] == "JOIN":
							juid = data.split()[0][1:]
							jchan = data.split()[2][1:]
							self.query("insert into chanlist value ('%s', '%s')" % (juid, _mysql.escape_string(jchan)))
							
							if self.suspended(jchan):
								self.kick(jchan, juid, "Suspended: "+self.suspended(jchan))
								
							if self.chanexist(jchan):
								self.enforcebans(jchan)
								
							if self.chanflag("l", jchan):
								self.showlog(juid, jchan)
								self.log(juid, "join", jchan)
								
							fjoin_user = self.auth(juid)
							hasflag = False
							
							for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (_mysql.escape_string(jchan), _mysql.escape_string(fjoin_user))):
								if flag["flag"] == "n" or flag["flag"] == "q":
									self.mode(jchan, "+qo " + juid + " " + juid)
									hasflag = True
								elif flag["flag"] == "a":
									self.mode(jchan, "+ao " + juid + " " + juid)
									hasflag = True
								elif flag["flag"] == "o":
									self.mode(jchan, "+o " + juid)
									hasflag = True
								elif flag["flag"] == "h":
									self.mode(jchan, "+h " + juid)
									hasflag = True
								elif flag["flag"] == "v":
									self.mode(jchan, "+v " + juid)
									hasflag = True
								elif flag["flag"] == "b":
									self.kick(jchan, juid, "Banned.")
									hasflag = True
									
							if not hasflag:
								if self.chanflag("v", jchan):
									self.mode(jchan, "+v %s" % juid)
									
							for welcome in self.query("select name,welcome from channelinfo where name = '{0}'".format(_mysql.escape_string(jchan))):
								if self.chanflag("w", jchan):
									self.msg(juid, "[{0}] {1}".format(welcome["name"], welcome["welcome"]))
									
							if self.isoper(juid) and self.chanexist(jchan):
								self.send(":%s NOTICE %s :Operator %s has joined" % (self.services_id, jchan, self.nick(juid)))
						elif data.split()[1] == "FJOIN":
							fjoin_chan = data.split()[2]
							fjoin_nick = data.split()[5][1:]
							
							if fjoin_nick.find(",") != -1:
								fjoin_nick = fjoin_nick.split(",")[1]
								
							for pnick in data.split()[5:]:
								if pnick.find(",") != -1:
									pnick = pnick.split(",")[1]
									
								self.query("insert into chanlist value ('{0}','{1}')".format(_mysql.escape_string(pnick), _mysql.escape_string(fjoin_chan)))
								
								if self.suspended(fjoin_chan):
									if not self.isoper(pnick):
										self.kick(fjoin_chan, pnick, "Suspended: "+self.suspended(fjoin_chan))
									else:
										self.msg(fjoin_chan, "This channel is suspended: "+self.suspended(fjoin_chan))
										
							if self.chanexist(fjoin_chan):
								self.enforcebans(fjoin_chan)
								
							if self.chanflag("l", fjoin_chan):
								self.showlog(fjoin_nick, fjoin_chan)
								self.log(fjoin_nick, "join", fjoin_chan)
								
							fjoin_user = self.auth(fjoin_nick)
							hasflag = False
							
							for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (_mysql.escape_string(fjoin_chan), fjoin_user)):
								if flag["flag"] == "n" or flag["flag"] == "q":
									self.mode(fjoin_chan, "+qo " + fjoin_nick + " " + fjoin_nick)
									hasflag = True
								elif flag["flag"] == "a":
									self.mode(fjoin_chan, "+ao " + fjoin_nick + " " + fjoin_nick)
									hasflag = True
								elif flag["flag"] == "o":
									self.mode(fjoin_chan, "+o " + fjoin_nick)
									hasflag = True
								elif flag["flag"] == "h":
									self.mode(fjoin_chan, "+h " + fjoin_nick)
									hasflag = True
								elif flag["flag"] == "v":
									self.mode(fjoin_chan, "+v " + fjoin_nick)
									hasflag = True
								elif flag["flag"] == "b":
									self.kick(fjoin_chan, fjoin_nick, "Banned.")
									hasflag = True
									
							if not hasflag:
								if self.chanflag("v", fjoin_chan):
									self.mode(fjoin_chan, "+v %s" % fjoin_nick)
									
							for welcome in self.query("select name,welcome from channelinfo where name = '{0}'".format(_mysql.escape_string(fjoin_chan))):
								if self.chanflag("w", fjoin_chan):
									self.msg(fjoin_nick, "[{0}] {1}".format(welcome["name"], welcome["welcome"]))
									
							if self.isoper(fjoin_nick) and self.chanexist(fjoin_chan):
								self.send(":%s NOTICE %s :Operator %s has joined" % (self.services_id, fjoin_chan, self.nick(fjoin_nick)))
						elif data.split()[1] == "PART":
							pnick = data.split()[0][1:]
							pchan = data.split()[2]
							
							for parted in self.query("select channel from ipchan where ip = '%s' and channel = '%s'" % (self.getip(pnick), _mysql.escape_string(pchan))):
								self.send(":%s SVSJOIN %s %s" % (self.bot, pnick, parted["channel"]))
								self.msg(pnick, "Your IP is forced to be in "+parted["channel"])
								
							self.query("delete from chanlist where uid = '{0}' and channel = '{1}'".format(pnick, _mysql.escape_string(pchan)))
							
							if self.chanflag("l", pchan):
								if len(data.split()) == 3:
									self.log(pnick, "part", pchan)
								else:
									self.log(pnick, "part", pchan, ' '.join(data.split()[3:])[1:])
						elif data.split()[1] == "OPERTYPE":
							uid = data.split()[0][1:]
							self.query("insert into opers values ('%s')" % uid)
						elif data.split()[1] == "METADATA":
							if len(data.split()) == 5 and len(data.split()[4]) != 1:
								uid = data.split()[2]
								string = data.split()[3]
								content = ' '.join(data.split()[4:])[1:]
								self.metadata(uid, string, content)
						elif data.split()[1] == "IDLE":
							if len(data.split()) == 3:
								self.send(":{uid} IDLE {source} 0 0".format(uid=data.split()[2], source=data.split()[0][1:]))
						elif data.split()[1] == "MODE":
							smodes = data.split()[3]
							
							if smodes.find("+") != -1:
								smodes = smodes.split("+")[1]
								
								if smodes.find("-") != -1:
									smodes = smodes.split("-")[0]
									
								if smodes.find("B") != -1:
									crypthost = self.encode_md5(data.split()[0][1:] + ":" + self.nick(data.split()[0][1:]) + "!" + self.userhost(data.split()[0][1:]))
									self.send(":%s CHGHOST %s %s.gateway.%s" % (self.services_id, data.split()[0][1:], crypthost, '.'.join(self.services_name.split(".")[-2:])))
									self.query("insert into gateway values ('%s')" % data.split()[0][1:])
									
							smodes = data.split()[3]
							
							if smodes.find("-") != -1:
								smodes = smodes.split("-")[1]
								
								if smodes.find("+") != -1:
									smodes = smodes.split("+")[0]
									
								if smodes.find("B") != -1:
									self.send(":%s CHGHOST %s %s" % (self.bot, data.split()[0][1:], self.gethost(data.split()[0][1:])))
									self.query("delete from gateway where uid = '%s'" % data.split()[0][1:])
						elif data.split()[1] == "UID":
							self.query("delete from temp_nick where nick = '%s'" % data.split()[2])
							self.query("delete from gateway where uid = '%s'" % data.split()[2])
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
									
							if conns > limit and data.split()[8] != "0.0.0.0" and limit != 0:
								for nick in nicks:
									self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
									
								self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.bot, data.split()[8], limit))
							elif conns == limit and data.split()[8] != "0.0.0.0":
								for nick in nicks:
									self.msg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
									
							for ip in self.query("select channel from ipchan where ip = '%s'" % data.split()[8]):
								self.send(":%s SVSJOIN %s %s" % (self.bot, data.split()[2], ip["channel"]))
								
							if data.split()[10].find("B") != -1:
								crypthost = self.encode_md5(data.split()[2] + ":" + self.nick(data.split()[2]) + "!" + self.userhost(data.split()[2]))
								self.send(":%s CHGHOST %s %s.gateway.%s" % (self.services_id, data.split()[2], crypthost, '.'.join(self.services_name.split(".")[-2:])))
								self.query("insert into gateway values ('%s')" % data.split()[2])
		except Exception:
			et, ev, tb = sys.exc_info()
			e = "{0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
			debug(red("*") + " <<ERROR>> " + str(e))
			
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
			if len(text.split()) > 0:
				cmd = text.lower().split()[0]
				arg = list()
				args = ""
				
				if len(text.split()) > 1:
					arg = text.split()[1:]
					args = ' '.join(text.split()[1:])
					
				if cmd == "help":
					self.msg(source, "The following commands are available to you.")
					
					if len(args) != 0:
						if fnmatch.fnmatch("help", "*" + args.lower() + "*"):
							self.help(source, "HELP", "Shows information about all commands that are available to you")
					else:
						self.help(source, "HELP", "Shows information about all commands that are available to you")
						
					for command in dir(commands):
						if command != "__init__" and os.access("commands/"+command+".py", os.F_OK):
							exec("cmd_auth = commands.%s.%s().nauth" % (command, command))
							exec("cmd_oper = commands.%s.%s().oper" % (command, command))
							exec("cmd_help = commands.%s.%s().help" % (command, command))
							
							if not cmd_auth and not cmd_oper:
								if len(args) != 0:
									if fnmatch.fnmatch(command.lower(), "*" + args.lower() + "*"):
										self.help(source, command, cmd_help)
								else:
									self.help(source, command, cmd_help)
							elif cmd_auth and not cmd_oper and self.auth(source):
								if len(args) != 0:
									if fnmatch.fnmatch(command.lower(), "*" + args.lower() + "*"):
										self.help(source, command, cmd_help)
								else:
									self.help(source, command, cmd_help)
									
					if self.isoper(source):
						self.msg(source)
						self.msg(source, "For operators:")
						
						for command in dir(commands):
							if command != "__init__" and os.access("commands/"+command+".py", os.F_OK):
								exec("cmd_oper = commands.%s.%s().oper" % (command, command))
								exec("cmd_help = commands.%s.%s().help" % (command, command))
								
								if cmd_oper and self.isoper(source):
									if len(args) != 0:
										if fnmatch.fnmatch(command.lower(), "*" + args.lower() + "*"):
											self.help(source, command, cmd_help)
									else:
										self.help(source, command, cmd_help)
										
						if len(args) != 0:
							if fnmatch.fnmatch("reload", "*" + args.lower() + "*"):
								self.help(source, "RELOAD", "Reloads the config")
						else:
							self.help(source, "RELOAD", "Reloads the config")
							
						if len(args) != 0:
							if fnmatch.fnmatch("update", "*" + args.lower() + "*"):
								self.help(source, "UPDATE", "Updates the services")
						else:
							self.help(source, "UPDATE", "Updates the services")
							
						if len(args) != 0:
							if fnmatch.fnmatch("restart", "*" + args.lower() + "*"):
								self.help(source, "RESTART", "Restarts the services")
						else:
							self.help(source, "RESTART", "Restarts the services")
							
						if len(args) != 0:
							if fnmatch.fnmatch("quit", "*" + args.lower() + "*"):
								self.help(source, "QUIT", "Shutdowns the services")
						else:
							self.help(source, "QUIT", "Shutdowns the services")
							
						self.msg(source)
						
					self.msg(source, "End of list.")
				elif cmd == "reload" and self.isoper(source):
					config.read("config.cfg")
					self.debug = config.get("OTHER", "debug")
					self.email = config.get("OTHER", "email")
					self.regmail = config.get("OTHER", "regmail")
					reload(commands)
					self.msg(source, "Done.")
				elif cmd == "update" and self.isoper(source):
					_web = urllib2.urlopen("https://raw.github.com/Pythonz/PyServ/master/version")
					_version = _web.read()
					_web.close()
					
					if open("version", "r").read() != _version:
						_updates = len(os.listdir("sql/updates"))
						_hash = self.encode(open("pyserv.py", "r").read())
						_modules = list()
						
						for module in dir(commands):
							if os.access("commands/"+module+".py", os.F_OK):
								_modules.append(module)
								
						self.msg(source, "{0} -> {1}".format(open("version", "r").read(), _version))
						shell("git add config.cfg")
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
										
						if _hash != self.encode(open("pyserv.py", "r").read()):
							self.msg(source, "Done.")
							self.msg(source, "Restart ...")
							msg = "Services are going down for an update. Please be patient."
							self.send(":%s QUIT :%s" % (self.bot, msg))
							self.send(":%s SQUIT %s" % (self.services_id, self.services_name))
							self.con.close()
							
							if os.access("pyserv.pid", os.F_OK):
								shell("sh pyserv restart")
							else:
								sys.exit(0)
						else:
							self.msg(source, "Reload ...")
							reload(commands)
							
							for module in _modules:
								if not os.access("commands/"+module+".py", os.F_OK):
									exec("del commands."+module)
									exec("""del sys.modules["commands.%s"]""" % module)
									
							self.msg(source, "Done.")
					else:
						self.msg(source, "No update available.")
				elif cmd == "restart" and self.isoper(source):
					if len(arg) == 0:
						msg = "Services are going down for a restart. Please be patient."
						self.send(":%s QUIT :%s" % (self.bot, msg))
					else:
						self.send(":%s QUIT :%s" % (self.bot, args))
						
					self.send(":%s SQUIT %s" % (self.services_id, self.services_name))
					self.con.close()
					
					if os.access("pyserv.pid", os.F_OK):
						shell("sh pyserv restart")
					else:
						sys.exit(0)
				elif cmd == "quit" and self.isoper(source):
					if os.access("pyserv.pid", os.F_OK):
						if len(arg) == 0:
							msg = "Services are going offline."
							self.send(":%s QUIT :%s" % (self.bot, msg))
						else:
							self.send(":%s QUIT :%s" % (self.bot, args))
							
						self.send(":%s SQUIT %s" % (self.services_id, self.services_name))
						self.con.close()
						shell("sh pyserv stop")
					else:
						self.msg(source, "You are running in debug mode, only restart is possible!")
				else:
					self.msg(source, "Unknown command {0}. Please try HELP for more information.".format(text.split()[0].upper()))
			else:
				self.msg(source, "Unknown command NULL. Please try HELP for more information.")
		except Exception:
			self.msg(source, "An error has occured. The Development-Team has been notified about this problem.")
			et, ev, tb = sys.exc_info()
			e = "{0}: {1} (Line #{2})".format(et, ev, traceback.tb_lineno(tb))
			if self.email != "":
				self.mail("mechi.community@yahoo.de", "From: {0} <{1}>\nTo: PyServ Development <mechi.community@yahoo.de>\nSubject: Bug on {0}\n{2}".format(self.services_description, self.email, str(e)))
				
			debug(red("*") + " <<MSG-ERROR>> "+str(e))

	def uid (self, nick):
		if nick == self.bot_nick:
			return self.bot
			
		for data in self.query("select uid from online where nick = '{0}'".format(nick)):
			return str(data["uid"])
			
		return nick

	def nick (self, source):
		if source == self.bot:
			return self.bot_nick
			
		for data in self.query("select nick from online where uid = '%s'" % source):
			return str(data["nick"])
			
		return source

	def user (self, user):
		if user.lower() == self.bot_nick.lower():
			return self.bot_nick
			
		for data in self.query("select name from users where name = '%s'" % user):
			return str(data["name"])
			
		return False

	def banned(self, user):
		for data in self.query("select * from users where name = '%s' and suspended != '0'" % user):
			return data["suspended"]
			
		return False

	def gateway (self, target):
		uid = self.uid(target)
		
		for data in self.query("select uid from gateway where uid = '%s'" % uid):
			return True
			
		return False

	def send(self, text):
		self.con.send(text+"\n")
		debug(blue("*") + " " + text)

	def push(self, target, message):
		self.send(":{uid} PUSH {target} ::{message}".format(uid=self.services_id, target=target, message=message))

	def help(self, target, command, description=""):
		self.msg(target, command.upper()+" "*int(20-len(command))+description)

	def ison(self, user):
		for data in self.query("select * from temp_nick where user = '%s'" % user):
			return True
			
		return False

	def usermodes(self, target):
		user = self.auth(target)
		
		if self.ison(user):
			for data in self.query("select modes from users where name = '%s'" % user):
				self.mode(target, data["modes"])
				
				if data["modes"].find("+") != -1:
					modes = data["modes"].split("+")[1]
					
					if modes.find("-") != -1:
						modes = modes.split("-")[0]
						
					if modes.find("B") != -1:
						if not self.gateway(target):
							self.query("insert into gateway values ('%s')" % target)
							self.vhost(target)
							
				if data["modes"].find("-") != -1:
					modes = data["modes"].split("-")[1]
					
					if modes.find("+") != -1:
						modes.split("+")[0]
						
					if modes.find("B") != -1:
						if self.gateway(target):
							self.query("delete from gateway where uid = '%s'" % target)
							self.vhost(target)

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

	def msg(self, target, text=" ", action=False):
		if self.userflag(target, "n") and not action:
			self.send(":%s NOTICE %s :%s" % (self.bot, target, text))
		elif not self.userflag(target, "n") and not action:
			self.send(":%s PRIVMSG %s :%s" % (self.bot, target, text))
		else:
			self.send(":%s PRIVMSG %s :\001ACTION %s\001" % (self.bot, target, text))

	def mode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.bot, target, mode))
		
		if target.startswith("#"):
			if self.chanflag("l", target):
				self.log(self.bot_nick, "mode", target, mode)

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
			online = False
			
			for source in self.sid(user):
				online = True
				self.msg(source, "[Memo] From: %s, Message: %s" % (data["source"], data["message"]))
				
			if online:
				self.query("delete from memo where user = '%s' and source = '%s' and message = '%s'" % (user, data["source"], _mysql.escape_string(data["message"])))

	def chanexist(self, channel):
		for data in self.query("select name from channelinfo where name = '%s'" % channel):
			return True
			
		return False

	def join(self, channel):
		if self.chanexist(channel) and not self.suspended(channel):
			self.send(":%s JOIN %s" % (self.bot, channel))
			self.mode(channel, "+rqo {0} {0}".format(self.bot))

	def statistics(self):
		stats = dict()
		
		for data in self.query("select * from statistics"):
			stats[data["attribute"]] = data["value"]
			
		return stats

	def killcount(self):
		kills = int(self.statistics()["kills"])
		kills += 1
		self.query("update statistics set `value` = '%s' where attribute = 'kills'" % kills)
		return kills

	def kickcount(self):
		kicks = int(self.statistics()["kicks"])
		kicks += 1
		self.query("update statistics set `value` = '%s' where attribute = 'kicks'" % kicks)
		return kicks

	def kill(self, target, reason="You're violating network rules"):
		if target.lower() != self.bot_nick.lower() and not self.isoper(self.uid(target)):
			self.send(":%s KILL %s :Killed (*.%s (%s (#%s)))" % (self.bot, target, '.'.join(self.services_name.split(".")[-2:]), reason, str(self.killcount())))

	def vhost(self, target):
		if not self.gateway(target):
			entry = False
			
			for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
				entry = True
				vhost = str(data["vhost"])
				
				if str(data["vhost"]).find("@") != -1:
					vident = vhost.split("@")[0]
					vhost = vhost.split("@")[1]
					self.send(":%s CHGIDENT %s %s" % (self.bot, target, vident))
					
				self.send(":%s CHGHOST %s %s" % (self.bot, target, vhost))
				self.msg(target, "Your vhost %s has been activated" % data["vhost"])
				
			if not entry:
				self.send(":%s CHGIDENT %s %s" % (self.bot, target, self.userhost(target).split("@")[0]))
				self.send(":%s CHGHOST %s %s" % (self.bot, target, self.gethost(target)))
		else:
			username = self.userhost(target).split("@")[0]
			self.send(":%s CHGIDENT %s %s" % (self.bot, target, username))
			crypthost = self.encode_md5(target + ":" + self.nick(target) + "!" + self.userhost(target))
			self.send(":%s CHGHOST %s %s.gateway.%s" % (self.services_id, target, crypthost, '.'.join(self.services_name.split(".")[-2:])))
			self.msg(target, "Your vhost %s.gateway.%s has been activated" % (crypthost, '.'.join(self.services_name.split(".")[-2:])))

	def flag(self, target):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag,channel from channels where user = '%s' order by channel" % str(data["user"])):
				if flag["flag"] == "n" or flag["flag"] == "q":
					self.mode(flag["channel"], "+qo " + target + " " + target)
				elif flag["flag"] == "a":
					self.mode(flag["channel"], "+ao " + target + " " + target)
				elif flag["flag"] == "o":
					self.mode(flag["channel"], "+o " + target)
				elif flag["flag"] == "h":
					self.mode(flag["channel"], "+h " + target)
				elif flag["flag"] == "v":
					self.mode(flag["channel"], "+v " + target)
				elif flag["flag"] == "b":
					self.kick(flag["channel"], target, "Banned.")

	def autojoin(self, target):
		user = self.auth(target)
		
		if self.ison(user):
			if self.userflag(target, "a"):
				for data in self.query("select channel,flag from channels where user = '%s'" % user):
					channel = data["channel"]
					flag = data["flag"]
					
					if flag == "n" or flag == self.bot_nick or flag == "a" or flag == "o" or flag == "h" or flag == "v":
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

	def encode(self, string):
		return hashlib.sha512(string).hexdigest()

	def encode_md5(self, string):
		return hashlib.md5(string).hexdigest()

	def query(self, string):
		self.db.query(str(string))
		result = self.db.store_result()
		
		if result:
			results = list()
			
			for data in result.fetch_row(maxrows=0, how=1):
				results.append(data)
				
			return results

	def query_row(self, string):
		self.db.query(str(string))
		result = self.db.store_result()
		
		if result:
			for data in result.fetch_row(maxrows=1, how=1):
				return data

	def mail(self, receiver, message):
		try:
			mail = smtplib.SMTP('127.0.0.1', 25)
			mail.sendmail(self.email, ['%s' % receiver], message)
			mail.quit()
		except Exception,e:
			debug(red("*") + " <<MAIL-ERROR>> "+str(e))

	def log(self, source, msgtype, channel, text=""):
		try:
			if msgtype.lower() == "mode" and len(text.split()) > 1:
				nicks = list()
				
				for nick in text.split()[1:]:
					nicks.append(self.nick(nick))
					
				text = "{text} {nicks}".format(text=text.split()[0], nicks=' '.join(nicks))
				
			if source == self.bot_nick:
				sender = self.bot_nick+"!"+self.bot_user+"@"+self.services_name
			else:
				sender = self.nick(source)+"!"+self.userhost(source)
				
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
		except:
			pass

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
		except:
			pass

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
		
		if days > 0:
			return "%s days %s hours %s minutes %s seconds" % (days, hours, minutes, seconds)
			
		if hours > 0:
			return "%s hours %s minutes %s seconds" % (hours, minutes, seconds)
			
		if minutes > 0:
			return "%s minutes %s seconds" % (minutes, seconds)
			
		return "%s seconds" % seconds

	def kick(self, channel, target, reason="Requested."):
		uid = self.uid(target)
		
		if self.onchan(channel, target):
			if self.chanflag("c", channel):
				self.send(":{uid} KICK {channel} {target} :{reason} (#{count})".format(uid=self.bot, target=uid, channel=channel, reason=reason, count=str(self.kickcount())))
			else:
				self.send(":{uid} KICK {channel} {target} :{reason}".format(uid=self.bot, target=uid, channel=channel, reason=reason))
				self.kickcount()
				
			self.query("delete from chanlist where channel = '{0}' and uid = '{1}'".format(channel, uid))

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
		if target != "*!*@*":
			for user in self.userlist(channel):
				if self.gateway(user):
					crypthost = self.encode_md5(user + ":" + self.nick(user) + "!" + self.userhost(user))+".gateway."+'.'.join(self.services_name.split(".")[-2:])
					
					if fnmatch.fnmatch(self.nick(user)+"!"+self.userhost(user).split("@")[0]+"@"+crypthost, target):
						self.mode(channel, "+b "+target)
						self.kick(channel, user, "Banned.")
						
				for hostmask in self.hostmask(user):
					if fnmatch.fnmatch(hostmask, target):
						self.mode(channel, "+b "+target)
						self.kick(channel, user, "Banned.")

	def enforcebans(self, channel):
		for data in self.query("select ban from banlist where channel = '%s'" % channel):
			if data["ban"] != "*!*@*":
				for user in self.userlist(channel):
					if self.gateway(user):
						crypthost = self.encode_md5(user + ":" + self.nick(user) + "!" + self.userhost(user))+".gateway."+'.'.join(self.services_name.split(".")[-2:])
						
						if fnmatch.fnmatch(self.nick(user)+"!"+self.userhost(user).split("@")[0]+"@"+crypthost, data["ban"]):
							self.mode(channel, "+b "+data["ban"])
							self.kick(channel, user, "Banned.")
							
					for hostmask in self.hostmask(user):
						if fnmatch.fnmatch(hostmask, data["ban"]):
							self.mode(channel, "+b "+data["ban"])
							self.kick(channel, user, "Banned.")

	def checkbans(self, channel, bans):
		if self.chanflag("e", channel):
			for ban in bans.split():
				if fnmatch.fnmatch(ban, "*!*@*") and ban != "*!*@*":
					for user in self.userlist(channel):
						if self.gateway(user):
							crypthost = self.encode(user + ":" + self.nick(user) + "!" + self.userhost(user))+".gateway."+'.'.join(self.services_name.split(".")[-2:])
							
							if fnmatch.fnmatch(self.nick(user)+"!"+self.userhost(user).split("@")[0]+"@"+crypthost, ban):
								self.kick(channel, user, "Banned.")
								
						for hostmask in self.hostmask(user):
							if fnmatch.fnmatch(hostmask, ban):
								self.kick(channel, user, "Banned.")
								
						for ip in self.getip(user):
							if fnmatch.fnmatch("*!*@"+ip, ban):
								self.kick(channel, user, "Banned.")
				elif ban == "*!*@*":
					self.mode(channel, "-b *!*@*")

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
		for data in self.query("select reason from suspended where channel = '%s'" % _mysql.escape_string(channel)):
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

	def scanport(self, host, port):
		try:
			scpo = socket.socket()
			scpo.settimeout(1)
			scpo.connect((str(host), int(port)))
			scpo.close()
			return True
		except socket.error:
			return False

	def fantasy(self, channel):
		if self.chanexist(channel):
			for data in self.query("select fantasy from channelinfo where name = '%s'" % _mysql.escape_string(channel)):
				return data["fantasy"]
				
		return False

class Command:
	import sys
	import os
	import ConfigParser
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
		self.con = con
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
		self.status = config.getboolean("FAILOVER", "active")
		self.regmail = config.get("OTHER", "regmail")
		self.bot = "%sAAAAAA" % self.services_id
		self.bot_nick = config.get("BOT", "nick").split()[0]
		self.bot_user = config.get("BOT", "user").split()[0]
		self.bot_real = config.get("BOT", "real")

	def onCommand(self, uid, arguments):
		pass

	def onFantasy(self, uid, channel, arguments):
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
			
		Smysql.close()

	def query_row(self, string):
		Smysql = _mysql.connect(host=self.mysql_host, port=self.mysql_port, db=self.mysql_name, user=self.mysql_user, passwd=self.mysql_passwd)
		Smysql.query(str(string))
		result = Smysql.store_result()
		
		if result:
			for data in result.fetch_row(maxrows=1, how=1):
				Smysql.close()
				return data
				
		Smysql.close()

	def uid (self, nick):
		if nick == self.bot_nick:
			return self.bot
			
		for data in self.query("select uid from online where nick = '{0}'".format(nick)):
			return data["uid"]
			
		return nick

	def nick (self, source):
		if source == self.bot:
			return self.bot_nick
			
		for data in self.query("select nick from online where uid = '%s'" % source):
			return data["nick"]
			
		return source

	def user (self, user):
		if user.lower() == self.bot_nick.lower():
			return self.bot_nick
			
		for data in self.query("select name from users where name = '%s'" % user):
			return str(data["name"])
			
		return False

	def banned(self, user):
		for data in self.query("select * from users where name = '%s' and suspended != '0'" % user):
			return data["suspended"]
			
		return False

	def gateway (self, target):
		uid = self.uid(target)
		
		for data in self.query("select uid from gateway where uid = '%s'" % uid):
			return True
			
		return False

	def push(self, target, message):
		self.send(":{uid} PUSH {target} ::{message}".format(uid=self.services_id, target=target, message=message))

	def help(self, target, command, description=""):
		self.msg(target, command.upper()+" "*int(20-len(command))+description)

	def ison(self, user):
		for data in self.query("select * from temp_nick where user = '%s'" % user):
			return True
			
		return False

	def usermodes(self, target):
		user = self.auth(target)
		
		if self.ison(user):
			for data in self.query("select modes from users where name = '%s'" % user):
				self.mode(target, data["modes"])
				
				if data["modes"].find("+") != -1:
					modes = data["modes"].split("+")[1]
					
					if modes.find("-") != -1:
						modes = modes.split("-")[0]
						
					if modes.find("B") != -1:
						if not self.gateway(target):
							self.query("insert into gateway values ('%s')" % target)
							self.vhost(target)
							
				if data["modes"].find("-") != -1:
					modes = data["modes"].split("-")[1]
					
					if modes.find("+") != -1:
						modes.split("+")[0]
						
					if modes.find("B") != -1:
						if self.gateway(target):
							self.query("delete from gateway where uid = '%s'" % target)
							self.vhost(target)

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

	def msg(self, target, text=" ", action=False):
		if self.userflag(target, "n") and not action:
			self.send(":%s NOTICE %s :%s" % (self.bot, target, text))
		elif not self.userflag(target, "n") and not action:
			self.send(":%s PRIVMSG %s :%s" % (self.bot, target, text))
		else:
			self.send(":%s PRIVMSG %s :\001ACTION %s\001" % (self.bot, target, text))

	def mode(self, target, mode):
		self.send(":%s SVSMODE %s %s" % (self.bot, target, mode))
		
		if target.startswith("#"):
			if self.chanflag("l", target):
				self.log(self.bot_nick, "mode", target, mode)

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
			online = False
			
			for source in self.sid(user):
				online = True
				self.msg(source, "[Memo] From: %s, Message: %s" % (data["source"], data["message"]))
				
			if online:
				self.query("delete from memo where user = '%s' and source = '%s' and message = '%s'" % (user, data["source"], _mysql.escape_string(data["message"])))

	def chanexist(self, channel):
		for data in self.query("select name from channelinfo where name = '%s'" % channel):
			return True
			
		return False

	def join(self, channel):
		if self.chanexist(channel) and not self.suspended(channel):
			self.send(":%s JOIN %s" % (self.bot, channel))
			self.mode(channel, "+rqo {0} {0}".format(self.bot))

	def statistics(self):
		stats = dict()
		
		for data in self.query("select * from statistics"):
			stats[data["attribute"]] = data["value"]
			
		return stats

	def killcount(self):
		kills = int(self.statistics()["kills"])
		kills += 1
		self.query("update statistics set `value` = '%s' where attribute = 'kills'" % kills)
		return kills

	def kickcount(self):
		kicks = int(self.statistics()["kicks"])
		kicks += 1
		self.query("update statistics set `value` = '%s' where attribute = 'kicks'" % kicks)
		return kicks

	def kill(self, target, reason="You're violating network rules"):
		if target.lower() != self.bot_nick.lower() and not self.isoper(self.uid(target)):
			self.send(":%s KILL %s :Killed (*.%s (%s (#%s)))" % (self.bot, target, '.'.join(self.services_name.split(".")[-2:]), reason, str(self.killcount())))

	def vhost(self, target):
		if not self.gateway(target):
			entry = False
			
			for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % self.auth(target)):
				entry = True
				vhost = str(data["vhost"])
				
				if str(data["vhost"]).find("@") != -1:
					vident = vhost.split("@")[0]
					vhost = vhost.split("@")[1]
					self.send(":%s CHGIDENT %s %s" % (self.bot, target, vident))
					
				self.send(":%s CHGHOST %s %s" % (self.bot, target, vhost))
				self.msg(target, "Your vhost %s has been activated" % data["vhost"])
				
			if not entry:
				self.send(":%s CHGIDENT %s %s" % (self.bot, target, self.userhost(target).split("@")[0]))
				self.send(":%s CHGHOST %s %s" % (self.bot, target, self.gethost(target)))
		else:
			username = self.userhost(target).split("@")[0]
			self.send(":%s CHGIDENT %s %s" % (self.bot, target, username))
			crypthost = self.encode_md5(target + ":" + self.nick(target) + "!" + self.userhost(target))
			self.send(":%s CHGHOST %s %s.gateway.%s" % (self.services_id, target, crypthost, '.'.join(self.services_name.split(".")[-2:])))
			self.msg(target, "Your vhost %s.gateway.%s has been activated" % (crypthost, '.'.join(self.services_name.split(".")[-2:])))

	def flag(self, target):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag,channel from channels where user = '%s' order by channel" % str(data["user"])):
				if flag["flag"] == "n" or flag["flag"] == "q":
					self.mode(flag["channel"], "+qo " + target + " " + target)
				elif flag["flag"] == "a":
					self.mode(flag["channel"], "+ao " + target + " " + target)
				elif flag["flag"] == "o":
					self.mode(flag["channel"], "+o " + target)
				elif flag["flag"] == "h":
					self.mode(flag["channel"], "+h " + target)
				elif flag["flag"] == "v":
					self.mode(flag["channel"], "+v " + target)
				elif flag["flag"] == "b":
					self.kick(flag["channel"], target, "Banned.")

	def autojoin(self, target):
		user = self.auth(target)
		
		if self.ison(user):
			if self.userflag(target, "a"):
				for data in self.query("select channel,flag from channels where user = '%s'" % user):
					channel = data["channel"]
					flag = data["flag"]
					
					if flag == "n" or flag == self.bot_nick or flag == "a" or flag == "o" or flag == "h" or flag == "v":
						self.send(":%s SVSJOIN %s %s" % (self.bot, target, channel))

	def getflag(self, target, channel):
		for data in self.query("select user from temp_nick where nick = '%s'" % target):
			for flag in self.query("select flag from channels where channel = '%s' and user = '%s'" % (_mysql.escape_string(channel), data["user"])):
				return flag["flag"]
				
		return 0

	def chanflag(self, flag, channel):
		for data in self.query("select flags from channelinfo where name = '{0}'".format(_mysql.escape_string(channel))):
			if data["flags"].find(flag) != -1:
				return True
				
		return False

	def isoper(self, target):
		isoper = False
		
		for data in self.query("select * from opers where uid = '%s'" % target):
			isoper = True
			
		return isoper

	def encode(self, string):
		return hashlib.sha512(string).hexdigest()

	def encode_md5(self, string):
		return hashlib.md5(string).hexdigest()

	def mail(self, receiver, message):
		try:
			mail = smtplib.SMTP('127.0.0.1', 25)
			mail.sendmail(self.email, ['%s' % receiver], message)
			mail.quit()
		except Exception,e:
			debug(red("*") + " <<MAIL-ERROR>> "+str(e))

	def log(self, source, msgtype, channel, text=""):
		try:
			if msgtype.lower() == "mode" and len(text.split()) > 1:
				nicks = list()
				
				for nick in text.split()[1:]:
					nicks.append(self.nick(nick))
					
				text = "{text} {nicks}".format(text=text.split()[0], nicks=' '.join(nicks))
				
			if source == self.bot_nick:
				sender = self.bot_nick+"!"+self.bot_user+"@"+self.services_name
			else:
				sender = self.nick(source)+"!"+self.userhost(source)
				
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
		except:
			pass

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
		except:
			pass

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
		
		if days > 0:
			return "%s days %s hours %s minutes %s seconds" % (days, hours, minutes, seconds)
			
		if hours > 0:
			return "%s hours %s minutes %s seconds" % (hours, minutes, seconds)
			
		if minutes > 0:
			return "%s minutes %s seconds" % (minutes, seconds)
			
		return "%s seconds" % seconds

	def send(self, text):
		self.con.send(text+"\n")
		debug(blue("*") + " " + text)

	def metadata(self, uid, string, content):
		if string == "accountname":
			self.query("delete from temp_nick where nick = '%s' or user = '%s'" % (uid, _mysql.escape_string(content)))
			self.query("insert into temp_nick values ('%s','%s')" % (uid, _mysql.escape_string(content)))
			self.msg(uid, "You are now logged in as %s" % content)
			self.vhost(uid)
			self.flag(uid)
			self.memo(content)

	def kick(self, channel, target, reason="Requested."):
		uid = self.uid(target)
		
		if self.onchan(channel, target):
			if self.chanflag("c", channel):
				self.send(":{uid} KICK {channel} {target} :{reason} (#{count})".format(uid=self.bot, target=uid, channel=channel, reason=reason, count=str(self.kickcount())))
			else:
				self.send(":{uid} KICK {channel} {target} :{reason}".format(uid=self.bot, target=uid, channel=channel, reason=reason))
				self.kickcount()
				
			self.query("delete from chanlist where channel = '{0}' and uid = '{1}'".format(_mysql.escape_string(channel), uid))

	def userlist(self, channel):
		uid = list()
		
		for user in self.query("select uid from chanlist where channel = '%s'" % channel):
			uid.append(user["uid"])
			
		return uid

	def onchan(self, channel, target):
		uid = self.uid(target)
		
		for data in self.query("select * from chanlist where channel = '%s' and uid = '%s'" % (_mysql.escape_string(channel), uid)):
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
		if target != "*!*@*":
			for user in self.userlist(channel):
				if self.gateway(user):
					crypthost = self.encode_md5(user + ":" + self.nick(user) + "!" + self.userhost(user))+".gateway."+'.'.join(self.services_name.split(".")[-2:])
					
					if fnmatch.fnmatch(self.nick(user)+"!"+self.userhost(user).split("@")[0]+"@"+crypthost, target):
						self.mode(channel, "+b "+target)
						self.kick(channel, user, "Banned.")
						
				for hostmask in self.hostmask(user):
					if fnmatch.fnmatch(hostmask, target):
						self.mode(channel, "+b "+target)
						self.kick(channel, user, "Banned.")

	def enforcebans(self, channel):
		for data in self.query("select ban from banlist where channel = '%s'" % channel):
			if data["ban"] != "*!*@*":
				for user in self.userlist(channel):
					if self.gateway(user):
						crypthost = self.encode_md5(user + ":" + self.nick(user) + "!" + self.userhost(user))+".gateway."+'.'.join(self.services_name.split(".")[-2:])
						
						if fnmatch.fnmatch(self.nick(user)+"!"+self.userhost(user).split("@")[0]+"@"+crypthost, data["ban"]):
							self.mode(channel, "+b "+data["ban"])
							self.kick(channel, user, "Banned.")
							
					for hostmask in self.hostmask(user):
						if fnmatch.fnmatch(hostmask, data["ban"]):
							self.mode(channel, "+b "+data["ban"])
							self.kick(channel, user, "Banned.")

	def checkbans(self, channel, bans):
		if self.chanflag("e", channel):
			for ban in bans.split():
				if fnmatch.fnmatch(ban, "*!*@*") and ban != "*!*@*":
					for user in self.userlist(channel):
						if self.gateway(user):
							crypthost = self.encode_md5(user + ":" + self.nick(user) + "!" + self.userhost(user))+".gateway."+'.'.join(self.services_name.split(".")[-2:])
							
							if fnmatch.fnmatch(self.nick(user)+"!"+self.userhost(user).split("@")[0]+"@"+crypthost, ban):
								self.kick(channel, user, "Banned.")
								
						for hostmask in self.hostmask(user):
							if fnmatch.fnmatch(hostmask, ban):
								self.kick(channel, user, "Banned.")
								
						for ip in self.getip(user):
							if fnmatch.fnmatch("*!*@"+ip, ban):
								self.kick(channel, user, "Banned.")
				elif ban == "*!*@*":
					self.mode(channel, "-b *!*@*")

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
		for data in self.query("select reason from suspended where channel = '%s'" % _mysql.escape_string(channel)):
			return data["reason"]
			
		return False

	def userhost(self, target):
		uid = self.uid(target)
		
		for data in self.query("select username,host from online where uid = '%s'" % uid):
			return data["username"]+"@"+data["host"]
			
		return 0

	def getvhost(self, target):
		for data in self.query("select vhost from vhosts where user = '%s' and active = '1'" % _mysql.escape_string(target)):
			return data["vhost"]
			
		return "None"

	def scanport(self, host, port):
		try:
			scpo = socket.socket()
			scpo.settimeout(1)
			scpo.connect((str(host), int(port)))
			scpo.close()
			return True
		except socket.error:
			return False

	def fantasy(self, channel):
		if self.chanexist(channel):
			for data in self.query("select fantasy from channelinfo where name = '%s'" % _mysql.escape_string(channel)):
				return data["fantasy"]
				
		return False

class error(Exception):
	def __init__(self, value):
		self.value = value
		self.email = config.get("OTHER", "email")
	def __str__(self):
		try:
			mail = smtplib.SMTP('127.0.0.1', 25)
			mail.sendmail(self.email, ['mechi.community@yahoo.de'], str(self.value))
			mail.quit()
		except:
			pass
		finally:
			return repr(self.value)
		
def failover(timeout=1, inet=socket.AF_INET, stream=socket.SOCK_STREAM):
	try:
		if config.getboolean("FAILOVER", "active") and config.get("FAILOVER", "address") != "":
			sock = socket.socket(inet, stream)
			sock.settimeout(timeout)
			sock.connect((config.get("FAILOVER", "address"), 5556))
			sock.close()
			return True
		else:
			return False
	except:
		return False

if __name__ == "__main__":
	try:
		while True:
			__version__ = open("version", "r").read()
			
			if len(sys.argv) == 1:
				__config__ = "config.cfg"
			else:
				__config__ = sys.argv[1]
				
			if not failover():
				if not failover(10):
					print(green("*") + " PyServ (" + __version__ + ") started (config: " + __config__ + ")")
					Services().run()
					print(red("*") + " PyServ (" + __version__ + ") stopped (config: " + __config__ + ")")
					
			time.sleep(1)
	except Exception,e:
		print(red("*") + " " + str(e))
	except KeyboardInterrupt:
		print(red("*") + " Aborting ... STRG +C")
