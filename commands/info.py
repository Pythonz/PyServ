from pyserv import Command

class info(Command):
	help = "Shows all information about an user"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			if self.user(arg[0]):
				user = self.user(arg[0])
				for user in self.query("select name,email,flags,modes from users where name = '{0}'".format(user)):
					self.msg(uid, "-Information for account {0}:".format(user["name"]))
					online = list()
					userhosts = list()
					hosts = list()
					for uuid in self.sid(user["name"]):
						online.append(self.nick(uuid))
						userhosts.append(self.userhost(uuid))
						hosts.append(self.gethost(uuid))
					self.msg(uid, "Online Nicks  : {0}".format(' '.join(online)))
					self.msg(uid, "Hosts         : {0}".format(' '.join(hosts)))
					self.msg(uid, "User hosts    : {0}".format(' '.join(userhosts)))
					self.msg(uid, "User flags    : {0}".format(user["flags"]))
					self.msg(uid, "User modes    : {0}".format(user["modes"]))
					self.msg(uid, "Email address : {0}".format(user["email"]))
					self.msg(uid, "vHost         : {0}".format(self.getvhost(user["name"])))
					self.msg(uid, "Known on following channels:")
					self.msg(uid, "Channel              Flag")
					for channel in self.query("select channel,flag from channels where user = '{0}'".format(user["name"])):
						self.msg(uid, " {0}{1}{2}".format(channel["channel"], " "*int(20-len(channel["channel"])), channel["flag"]))
					self.msg(uid, "End of list.")
			else:
				self.msg(uid, "Can't find user " + arg[0] + ".")
		else:
			self.msg(uid, "Syntax: INFO <account>")