import pyserv

class sync(pyserv.Command):
	nauth = 1
	help = "Syncs your flags on all channels"
	def onCommand(self, source, args):
		self.flag(source)
		self.msg(source, "Done.")
