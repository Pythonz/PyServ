import pyserv

class whois(pyserv.Command):
	help = "Shows information about a user"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		entry = False
		if len(arg) == 1:
			if arg[0].startswith("#"):
				for user in self.query("select name,email from users where name = '{0}'".format(arg[0][1:])):
					entry = True
					self.msg(source, "-Information for account {0}:".format(user[0]))
					online = list()
					for uid in self.query("select nick from temp_nick where user = '{0}'".format(user[0])):
						for data in self.query("select nick from online where uid = '{0}'".format(uid[0])):
							online.append(data[0])
					self.msg(source, "Online Nicks  : {0}".format(' '.join(online)))
					self.msg(source, "User flags    : {0}".format(self.userflags(user[0])))
					self.msg(source, "Email address : {0}".format(user[1]))
					self.msg(source, "vHost         : {0}".format(self.getvhost(user[0])))
					self.msg(source, "Known on following channels:")
					self.msg(source, "Channel              Flag")
					for channel in self.query("select channel,flag from channels where user = '{0}'".format(user[0])):
						self.msg(source, " {0}{1}{2}".format(channel[0], " "*int(20-len(channel[0])), channel[1]))
					self.msg(source, "End of list.")
			else:
				for data in self.query("select uid from online where nick = '{0}'".format(arg[0])):
					for user in self.query("select user from temp_nick where nick = '{0}'".format(data[0])):
						entry = True
						for account in self.query("select email from users where name = '{0}'".format(user[0])):
							self.msg(source, "-Information for account {0}:".format(user[0]))
							online = list()
							for uid in self.query("select nick from temp_nick where user = '{0}'".format(user[0])):
								for online_data in self.query("select nick from online where uid = '{0}'".format(uid[0])):
									online.append(online_data[0])
							self.msg(source, "Online Nicks  : {0}".format(' '.join(online)))
							self.msg(source, "User flags    : {0}".format(self.userflags(user[0])))
							self.msg(source, "Email address : {0}".format(account[0]))
							self.msg(source, "vHost         : {0}".format(self.getvhost(user[0])))
							self.msg(source, "Known on following channels:")
							self.msg(source, "Channel              Flag")
						for channel in self.query("select channel,flag from channels where user = '{0}'".format(user[0])):
							self.msg(source, " {0}{1}{2}".format(channel[0], " "*int(20-len(channel[0])), channel[1]))
						self.msg(source, "End of list.")
			if not entry:
				self.msg(source, "Can\'t find user {0}".format(arg[0]))
		else:
			self.msg(source, "Syntax: WHOIS <nick>/<#account>")
