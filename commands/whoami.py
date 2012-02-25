from pyserv import Command

class whoami(Command):
	help = "Shows information about you"
	nauth = 1
	def onCommand(self, uid, args):
		auth = self.auth(uid)
		for user in self.query("select name,email from users where name = '{0}'".format(auth)):
			self.msg(source, "-Information for account {0}:".format(user["name"]))
			online = list()
			for uid in self.sid(user["name"]):
				online.append(self.nick(uid))
			self.msg(source, "Online Nicks  : {0}".format(' '.join(online)))
			self.msg(source, "User flags    : {0}".format(self.userflags(user["name"])))
			self.msg(source, "Email address : {0}".format(user["email"]))
			self.msg(source, "vHost         : {0}".format(self.getvhost(user["name"])))
			self.msg(source, "Known on following channels:")
			self.msg(source, "Channel              Flag")
			for channel in self.query("select channel,flag from channels where user = '{0}'".format(user["name"])):
				self.msg(source, " {0}{1}{2}".format(channel["channel"], " "*int(20-len(channel["channel"])), channel["flag"]))
			self.msg(source, "End of list.")
