from pyserv import Command

class sahello(Command):
	help = "Creates an account for users"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 2:
			entry = False
			for data in self.query("select name from users where name = '%s'" % arg[0]):
				entry = True
			if not entry:
				self.query("insert into users values ('%s', '%s', 'Q@%s', 'n')" % (arg[0], self.hash(arg[1]), self.services_name))
				self.msg(uid, "Create account (%s, %s) ..." % (arg[0], arg[1]))
				self.msg(uid, "Done.")
			else:
				self.msg(uid, "%s is already in use." % arg[0])
		else:
			self.msg(uid, "Syntax: SAHELLO <account> <password>")
