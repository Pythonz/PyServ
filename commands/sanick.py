from pyserv import Command

class sanick(Command):
	help = "Change nicks of others"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 2:
			target = self.uid(arg[0])
			if target != arg[0] and target != self.bot:
				self.send(":" + self.bot + " SVSNICK " + target + " " + arg[1])
				self.msg(uid, "Done.")
			else:
				self.msg(uid, "Denied.")
		else:
			self.msg(uid, "Syntax: SANICK <nick> <newnick>")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, args)
