from pyserv import Command

class gline(Command):
	help = "G-Line actions"
	oper = 1

	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			if self.uid(arg[0]).lower() != arg[0].lower():
				if not self.isoper(self.uid(arg[0])):
					self.gline(arg[0])
					self.msg(uid, "Done.")
				else:
					self.msg(uid, "You cannot g-line an irc operator!")
			else:
				self.msg(uid, "Cannot find user '" + arg[0] + "' on the network.")
		elif len(arg) > 1:
			if self.uid(arg[0]).lower() != arg[0].lower():
				if not self.isoper(self.uid(arg[0])):
					self.gline(arg[0], ' '.join(arg[1:]))
					self.msg(uid, "Done.")
				else:
					self.msg(uid, "You cannot g-line an irc operator!")
			else:
				self.msg(uid, "Cannot find user '" + arg[0] + "' on the network.")
		else:
			self.msg(uid, "Syntax: GLINE <user> [<reason>]")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
