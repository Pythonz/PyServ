import pyserv

class ofeedback(pyserv.Command):
	help = "Reads the feedback from users"
	oper = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(args) == 0:
			self.msg(source, "Following users sent a feedback:")
			for data in self.query("select user from feedback"):
				self.msg(source, str(data[0]))
			self.msg(source, "To read a feedback: OFEEDBACK <user>")
		else:
			entry = False
			for data in self.query("select user,text from feedback"):
				if arg[0].lower() == str(data[0]).lower():
					entry = True
					self.msg(source, "[FEEDBACK]")
					self.msg(source, "FROM: %s" % str(data[0]))
					self.msg(source, "MESSAGE: " + str(data[1]))
					self.query("delete from feedback where user = '%s'" % str(data[0]))
			if not entry:
				self.msg(source, "There is no feedback from %s" % arg[0])
