from pyserv import Command

class sahello(Command):
	help = "Creates an account for users"
	oper = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 2:
			if arg[0].isalnum():
				entry = False
				
				for data in self.query("select name from users where name = '%s'" % arg[0]):
					entry = True
					
				if not entry:
					self.msg(uid, "Create account (%s, %s) ..." % (arg[0], arg[1]))
					self.query("insert into users (name,pass,email,flags,modes,suspended) values ('%s', '%s', '%s@%s', 'n', '+i', '0')" % (arg[0], self.encode(arg[1]), self.bot_nick, self.services_name))
					self.msg(uid, "Done.")
				else:
					self.msg(uid, "%s is already in use." % arg[0])
			else:
				self.msg(uid, "The nickname '" + arg[0] + "' contains invalid characters. Allowed are the characters A-z and 0-9.")
		else:
			self.msg(uid, "Syntax: SAHELLO <account> <password>")