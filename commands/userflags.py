from pyserv import Command

class userflags(Command):
	help = "Changes and shows your userflags"
	nauth = 1

	def onCommand(self, uid, args):
		mode = list()
		desc = list()
		mode.append("n")
		desc.append("%s will answer with notices, instead of privmsgs." % self.bot_nick)
		mode.append("a")
		desc.append("Autojoin all channels where you have chanflag +v or higher.")
		arg = args.split()
		
		if len(arg) == 0:
			self.msg(uid, "Current user flags: +"+self.userflags(uid))
		elif len(arg) == 1:
			if arg[0] == "?":
				i = 0
				
				while i != len(mode):
					self.msg(uid, mode[i]+" = "+desc[i])
					i += 1
			else:
				userflags = self.regexflag("+" + self.userflags(uid), arg[0])
				flags = ''.join([char for char in userflags if char in ''.join(mode)])
				self.query("update users set flags = '%s' where name = '%s'" % (flags, self.auth(uid)))
				self.msg(uid, "Done.")
		else:
			self.msg(uid, "Syntax: USERFLAGS [<flags>]")