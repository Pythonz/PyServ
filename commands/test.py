import pyserv

class test(pyserv.Command):
	def onCommand(self, uid, arguments):
		self.send("NOTICE {uid} :{arguments}".format(uid=uid, arguments=arguments))
