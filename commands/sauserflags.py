from pyserv import Command

class sauserflags(Command):
	help = "Changes and shows the userflags of other users"
	oper = 1

	def onCommand(self, uid, args):
		mode = list()
		desc = list()
		mode.append("n")
		desc.append("Q will answer with notices, instead of privmsgs.")
		mode.append("a")
		desc.append("Autojoin all channels where you have chanflag +v or higher.")
		arg = args.split()
		
		if len(arg) == 1:
			self.msg(uid, "Current user flags: "+self.userflags(self.uid(arg[0])))
		elif len(arg) == 2:
			if arg[0] == "?":
				i = 0
				
				while i != len(mode):
					self.msg(uid, mode[i]+" = "+desc[i])
					i += 1
			else:
				flags = ''.join([char for char in arg[1] if char in ''.join(mode)])
				self.query("update users set flags = '%s' where name = '%s'" % (flags, self.auth(self.uid(arg[0]))))
				self.msg(uid, "Done.")
		else:
			self.msg(uid, "Syntax: SAUSERFLAGS <user> [<flags>]")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
