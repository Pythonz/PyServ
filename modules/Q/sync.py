from pyserv import Command

class sync(Command):
	nauth = 1
	help = "Syncs your flags on all channels"

	def onCommand(self, source, args):
		self.flag(source)
		self.msg(source, "Done.")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
