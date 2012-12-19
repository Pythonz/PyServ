from pyserv import Command

class userflags(Command):
	help = "Changes and shows your userflags"
	nauth = 1

	def onCommand(self, uid, args):
		flags = list()
		mode.append("n")
		flags.append(["n", "{0} will answer with notice instead of query.".format(self.bot_nick)])
		flags.append(["a", "Autojoin all channels where you got chanlev +v or higher."])
		flags.append(["x", "Enable cloaked hosts"])
		arg = args.split()
		
		if len(arg) == 0:
			self.msg(uid, "Current user flags: +"+self.userflags(uid))
		elif len(arg) == 1:
			if arg[0] == "?":
				for flag in flags:
					self.msg(uid, "+{0} = {1}".format(flag[0], flag[1]))
			else:
				userflags = self.regexflag("+" + self.userflags(uid), arg[0])
				flags = ''.join([char for char in userflags if char in ''.join(mode)])
				self.query("update users set flags = '%s' where name = '%s'" % (flags, self.auth(uid)))
				self.msg(uid, "Done. Current user flags: +" + userflags)
				if arg[0].find("x") != -1:
					self.vhost(uid)
		else:
			self.msg(uid, "Syntax: USERFLAGS [<flags>]")