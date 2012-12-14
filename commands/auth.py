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
			
			for data in self.query("select name,pass,suspended from users where name = '%s'" % arg[0]):
				if self.encode(arg[1]) == str(data["pass"]):
					exists = True
					
					if data["suspended"] == "0":
						for user in self.query("select nick from temp_nick where user = '%s'" % str(data["name"])):
							self.msg(str(user["nick"]), "Warning: %s (%s) authed with your password." % (self.nick(source), self.userhost(source)))
							
						self.query("insert into temp_nick values ('%s','%s')" % (source, str(data["name"])))
						self.msg(source, "You are now logged in as %s" % str(data["name"]))
						self.msg(source, "Remember: NO-ONE from %s will ever ask for your password. NEVER send your password to ANYONE except %s@%s." % (self.services_description, self.bot_nick, self.services_name))
						self.meta(source, "accountname", str(data["name"]))
						self.usermodes(source)
						self.vhost(source)
						self.flag(source)
						self.autojoin(source)
						self.memo(str(data["name"]))
					else:
						self.msg(source, "Your account has been banned from " + self.services_description + ". Reason: " + data["suspended"])
						
			if not exists:
				self.msg(source, "Username or password incorrect.")
		else:
			self.msg(source, "Syntax: AUTH <username> <password>")
