from pyserv import Command

class feedback(Command):
	help = "Sends your feedback about us to us"
	nauth = 1
	def onCommand(self, source, args):
		import _mysql
		if len(args) > 0:
			entry = False
			for data in self.query("select text from feedback where user = '%s'" % self.auth(source)):
				entry = True
			if not entry:
				self.query("insert into feedback values('"+self.auth(source)+"','"+_mysql.escape_string(args)+"')")
				self.msg(source, "Feedback added to queue.")
				for op in self.query("select uid from opers"):
					self.msg(str(op["uid"]), "New feedback from %s" % self.auth(source))
			else:
				self.msg(source, "You already sent a feedback. Please wait until an operator read it.")
		else:
			self.msg(source, "FEEDBACK <text>")
