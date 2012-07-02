from pyserv import Command

class kill(Command):
	help = "Kills a user from the network"
	oper = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) == 1:
			self.kill(arg[0])
			self.msg(source, "Done.")
		elif len(arg) > 1:
			self.kill(arg[0], ' '.join(arg[1:]))
			self.msg(source, "Done.")
		else:
			self.msg(source, "Syntax: KILL <nick> [<reason>]")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
