from pyserv import Command

class userlist(Command):
	help = "Shows you a list of users in that channel"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				if self.chanexist(arg[0]):
					self.msg(uid, "Userlist for "+arg[0]+":")
					for user in self.userlist(arg[0]):
						self.msg(uid, "  "+self.nick(user)+" ("+self.userhost(user)+")")
					self.msg(uid, "End of list.")
				else: self.msg(uid, "Channel "+arg[0]+" is not known.")
			else: self.msg(uid, "Invalid channel: "+arg[0])
		else: self.msg(uid, "Syntax: USERLIST <#channel>")
