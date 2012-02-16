import pyserv

class hello(pyserv.Command):
	help = "Creates an account for you and sends the data to you"
	def onCommand(self, source, args):
		arg = args.split()
		if self.auth(source) != 0:
			self.msg(source, "HELLO is not available once you have authed.")
			return 0
		if len(arg) == 2:
			exists = False
			for data in self.query("select name from users where email = '%s' or name = '%s'" % (arg[0], self.nick(source))):
					exists = True
			if not exists:
				if arg[0].find("@") != -1 and arg[0].find(".") != -1 and arg[0].lower() == arg[1].lower():
					self.query("insert into users values ('%s','%s','%s')" % (self.nick(source), self.hash(hash(arg[0])), arg[0]))
					self.msg(source, "The account %s has been created successfully. You can login now with /msg Q auth account password" % self.nick(source))
					if self.regmail == "1":
						self.msg(source, "An email had been send to you with your password!")
						self.mail(arg[0], """From: %s <%s>\nTo: %s <%s>\nSubject: Your account on %s\n\nWelcome to %s\nYour account data:\n\nUser: %s\nPassword: %s\n\nAuth via "/msg Q auth %s %s"\nChange your password as soon as possible with "/msg Q newpass NEWPASS"!""" % (self.services_description, self.email, self.nick(source), arg[0], self.services_description, self.services_description, self.nick(source), hash(arg[0]), self.nick(source), hash(arg[0])))
					else:
						self.msg(source, """Use "/msg Q auth %s %s" to auth""" % (self.nick(source), hash(arg[0])))
						self.msg(source, "Change your password as soon as possible!")
				else:
					self.msg(source, "Invalid email %s!" % arg[0])
			else:
				self.msg(source, "The account %s already exists or your email %s is used!" % (self.nick(source),arg[0]))
		else:
			self.msg(source, "Syntax: HELLO <email> <email>")
