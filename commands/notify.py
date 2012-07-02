from pyserv import Command

class notify(Command):
	help = "Sends a global notify to all users on the network"
	oper = 1

	def onCommand(self, source, args):
		self.msg("$*", "[{nick}] {message}".format(nick=self.nick(source), message=args))
		self.msg(source, "Done.")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
