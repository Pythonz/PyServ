from pyserv import Command

class addline(Command):
	help = "TEST"
	oper = 1
	nauth = 1
	def onCommand(self, uid, args):
		self.send(":%s ADDLINE" % self.bot)
		self.msg(uid, "Done.")
