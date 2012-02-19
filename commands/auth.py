import pyserv

class auth(pyserv.Command):
	help = "Login with your account"
	def onCommand(self, source, args):
		arg = args.split()
		if self.auth(source) != 0:
			self.msg(source, "AUTH is not available once you have authed.");
			return 0
		if len(arg) == 2:
			exists = False
			for data in self.query("select name,pass from users where name = '%s'" % arg[0]):
				if self.hash(arg[1]) == str(data[1]):
					exists = True
					for user in self.query("select nick from temp_nick where user = '%s'" % str(data[0])):
						self.msg(str(user[0]), "Warning: %s (%s) authed with your password." % (self.nick(source), self.userhost(source)))
					self.query("insert into temp_nick values ('%s','%s')" % (source, str(data[0])))
					self.msg(source, "You are now logged in as %s" % str(data[0]))
					self.msg(source, "Remember: NO-ONE from %s will ever ask for your password.  NEVER send your password to ANYONE except Q." % self.services_description)
					self.meta(source, "accountname", str(data[0]))
					self.vhost(source)
					self.flag(source)
					self.memo(str(data[0]))
			if not exists:
				self.msg(source, "Wrong username or invalid password.")
		else:
			self.msg(source, "Syntax: AUTH <username> <password>")
