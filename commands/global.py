import pyserv

class global(pyserv.Command):
	help = "Sends a global message to all users on the network"
	oper = 1
	def onCommand(self, source, args):
		self.msg("$*", "[{nick}] {message}".format(nick=self.nick(source), message=args))
		self.msg(source, "Done.")
