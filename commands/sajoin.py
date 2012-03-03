from pyserv import Command

class sajoin(Command):
	help = "Forces a user to join a channel"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 2:
			self.send(":"+self.bot+" SVSJOIN "+self.uid(arg[1])+" "+arg[0])
			self.msg(uid, "Done.")
		else:
			self.msg(uid, "Syntax: SAJOIN <#channel> <nick>")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, channel + " " + args)
