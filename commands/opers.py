from pyserv import Command

class opers(Command):
	help = "Shows all operators available for help"
	def onCommand(self, uid, args):
		self.msg(uid, "Available operators:")
		for data in self.query("select uid from opers"):
			self.msg(uid, "  "+self.nick(data["uid"]))
		self.msg(uid, "End of list.")
