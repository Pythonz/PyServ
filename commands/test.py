import pyserv

class test(pyserv.Command):
	def onCommand(self, uid, arguments):
		self.msg(uid, arguments)
