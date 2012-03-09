from pyserv import Command

class fantasy(Command):
	help = "Define the fantasy prefix for your channel"
	nauth = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			if self.chanexist(arg[0]):
				flag = self.getflag(uid, arg[0])
				if flag == "n" or flag == "q" or flag == "a":
					if self.chanflag("f", arg[0]):
						self.msg(uid, "Current fantasy prefix for " + arg[0] + ": " + self.fantasy(arg[0]))
					else:
						self.msg(uid, "Fantasy commands are disabled for " + arg[0])
				else:
					self.msg(uid, "Denied.")
			else:
				self.msg(uid, "Invalid channel: " + arg[0])
		elif len(arg) == 2:
			if self.chanexist(arg[0]):
				flag = self.getflag(uid, arg[0])
				if flag == "n" or flag == "q" or flag == "a":
					if self.chanflag("f", arg[0]):
						self.query("update channelinfo set fantasy = '%s' where name = '%s'" % (arg[1], arg[0]))
						self.msg(uid, "Done.")
					else:
						self.msg(uid, "Fantasy commands are disabled for " + arg[0])
				else:
					self.msg(uid, "Denied.")
			else:
				self.msg(uid, "Invalid channel: " + arg[0])
		else:
			self.msg(uid, "Syntax: FANTASY <#channel> [<prefix>]")
