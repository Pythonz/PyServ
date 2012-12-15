from pyserv import Command

class gline(Command):
	help = "G-Line actions"
	oper = 1

	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			if self.uid(arg[0]).tolower() != arg[0].tolower():
				if not self.isoper(self.uid(arg[0])):
					self.gline(arg[0])
				else:
					self.msg(uid, "You cannot g-line another operator!")
			else:
				self.msg(uid, "Cannot find user '" + arg[0] + "' on the network.")
		elif len(arg) > 1:
			if self.uid(arg[0]).tolower() != arg[0].tolower():
				if not self.isoper(self.uid(arg[0])):
					self.gline(arg[0], ' '.join(arg[1:]))
				else:
					self.msg(uid, "You cannot g-line another operator!")
			else:
				self.msg(uid, "Cannot find user '" + arg[0] + "' on the network.")
		else:
			self.msg(uid, "Syntax: GLINE <user> [<reason>]")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
