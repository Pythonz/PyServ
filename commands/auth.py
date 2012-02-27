from pyserv import Command, config

class auth(Command):
	help = "Login with your account at " + config.get("BOT", "nick") + "@"+config.get("SERVICES", "name")
	def onCommand(self, source, args):
		arg = args.split()
		if self.auth(source) != 0:
			self.msg(source, "AUTH is not available once you have authed.")
			return 0
		if len(arg) == 2:
			exists = False
			for data in self.query("select name,pass from users where name = '%s'" % arg[0]):
				if self.encode(arg[1]) == str(data["pass"]):
					exists = True
					for user in self.query("select nick from temp_nick where user = '%s'" % str(data["name"])):
						self.msg(str(user["nick"]), "Warning: %s (%s) authed with your password." % (self.nick(source), self.userhost(source)))
					self.query("insert into temp_nick values ('%s','%s')" % (source, str(data["name"])))
					self.msg(source, "You are now logged in as %s" % str(data["name"]))
					self.msg(source, "Remember: NO-ONE from %s will ever ask for your password.  NEVER send your password to ANYONE except Q@%s." % (self.services_description, self.services_name))
					self.meta(source, "accountname", str(data["name"]))
					self.usermodes(source)
					self.vhost(source)
					self.flag(source)
					self.autojoin(source)
					self.memo(str(data["name"]))
			if not exists:
				self.msg(source, "Username or password incorrect.")
		else:
			self.msg(source, "Syntax: AUTH <username> <password>")

	def onFantasy(self, uid, chan, args):
		self.msg(uid, "WHAT THE HELL ARE YOU DOING?! \27NEVER\27 SEND AUTH WITH FANTASY!")
