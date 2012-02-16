import pyserv

class newpass(pyserv.Command):
	help = ""
	auth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			self.query("update users set pass = '%s' where name = '%s'" % (self.hash(arg[1]), self.auth(source)))
			self.msg(source, """Your new password is "%s". Remember it!""" % arg[1])
		else:
			self.msg(source, "Syntax: NEWPASS <password>")
