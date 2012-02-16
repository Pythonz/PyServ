import pyserv

class version(pyserv.Command):
	help = "Shows version of services"
	def onCommand(self, source, args):
		self.version(source)
