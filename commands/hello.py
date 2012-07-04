from pyserv import Command
from time import time
from _mysql import escape_string

class hello(Command):
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
					newpw = str(hash(str(time()) + arg[0] + arg[1]))
					self.query("insert into users (name,pass,email,flags,modes,suspended) values ('%s','%s','%s','n','+i','0')" % (self.nick(source), self.encode(newpw), escape_string(arg[0])))
					self.msg(source, "The account %s has been created successfully. You can login now with /msg Q auth account password" % self.nick(source))
					
					if self.regmail == "1":
						self.msg(source, "An email had been send to you with your password!")
						self.mail(arg[0], """From: %s <%s>\nTo: %s <%s>\nSubject: Your account on %s\n\nWelcome to %s\nYour account data:\n\nUser: %s\nPassword: %s\n\nAuth via "/MSG Q@%s AUTH %s %s"\nChange your password as soon as possible with "/MSG Q%s NEWPASS NEWPASS"!""" % (self.services_description, self.email, self.nick(source), arg[0], self.services_description, self.services_description, self.nick(source), newpw, self.services_name, self.nick(source), newpw, self.services_name))
					else:
						self.msg(source, """Use "/msg Q auth %s %s" to auth""" % (self.nick(source), newpw))
						self.msg(source, "Change your password as soon as possible!")
				else:
					self.msg(source, "Invalid email %s!" % arg[0])
			else:
				self.msg(source, "The account %s already exists or your email %s is used!" % (self.nick(source), arg[0]))
		else:
			self.msg(source, "Syntax: HELLO <email> <email>")
