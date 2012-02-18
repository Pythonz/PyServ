import pyserv

class kill(pyserv.Command):
	help = "Kills a user from the network"
	oper = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			self.kill(arg[0])
		elif len(arg) > 1:
			self.kill(arg[0], ' '.join(arg[1:]))
		else:
			self.msg(source, "Syntax: KILL <nick>")
