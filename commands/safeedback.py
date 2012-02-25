from pyserv import Command

class safeedback(Command):
	help = "Reads the feedback from users"
	oper = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(args) == 0:
			self.msg(source, "Following users sent a feedback:")
			for data in self.query("select user from feedback"):
				self.msg(source, "  "+str(data["user"]))
			self.msg(source, "To read a feedback: SAFEEDBACK <user>")
		else:
			entry = False
			for data in self.query("select user,text from feedback where user = '%s'" % arg[1]):
				entry = True
				self.msg(source, "[Feedback] From: %s Message: %s" % (data["user"], data["text"]))
				self.query("delete from feedback where user = '%s'" % str(data["user"]))
			if not entry:
				self.msg(source, "There is no feedback from %s" % arg[0])
