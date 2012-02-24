import pyserv

class ofeedback(pyserv.Command):
	help = "Reads the feedback from users"
	oper = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(args) == 0:
			self.msg(source, "Following users sent a feedback:")
			for data in self.query("select user from feedback"):
				self.msg(source, str(data["user"]))
			self.msg(source, "To read a feedback: OFEEDBACK <user>")
		else:
			entry = False
			for data in self.query("select user,text from feedback where user = '%s'" % arg[1]):
				entry = True
				self.msg(source, "\2[FEEDBACK]\2")
				self.msg(source, "\2FROM:\2 %s" % str(data["user"]))
				self.msg(source, "\2MESSAGE:\2 " + str(data["text"]))
				self.query("delete from feedback where user = '%s'" % str(data["user"]))
			if not entry:
				self.msg(source, "There is no feedback from %s" % arg[0])
