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
			if self.nick(source).isalnum():
				exists = False
				
				for data in self.query("select name from users where email = '%s' or name = '%s'" % (arg[0], self.nick(source))):
						exists = True
						
				if not exists:
					if arg[0].find("@") != -1 and arg[0].find(".") != -1 and arg[0].lower() == arg[1].lower():
						newpw = str(hash(str(time()) + arg[0] + arg[1]))
						self.query("insert into users (name,pass,email,flags,modes,suspended) values ('%s','%s','%s','n','+i','0')" % (self.nick(source), self.encode(newpw), escape_string(arg[0])))
						self.msg(source, "The account %s has been created successfully. You can login now with /msg %s@%s auth account password" % (self.nick(source), self.bot_nick, self.services_name))
						
						if self.regmail == "1":
							self.msg(source, "An email had been send to you with your password!")
							self.mail(arg[0], """From: {0} <{1}>\nTo: {2} <{3}>\nSubject: Your account on {4}\n\nWelcome to {4}\nYour account data:\n\nUser: {2}\nPassword: {5}\n\nAuth via "/MSG {6}@{7} AUTH {2} {5}"\nChange your password as soon as possible with "/MSG {6}@{7} NEWPASS <NEWPASSWORD>"!""".format(self.services_description, self.email, self.nick(source), arg[0], self.services_description, newpw, self.bot_nick, self.services_name))
						else:
							self.msg(source, """Use "/msg %s@%s auth %s %s" to auth""" % (self.bot_nick, self.services_name, self.nick(source), newpw))
							self.msg(source, "Change your password as soon as possible!")
					else:
						self.msg(source, "Invalid email %s!" % arg[0])
				else:
					self.msg(source, "The account %s already exists or your email %s is used!" % (self.nick(source), arg[0]))
			else:
				self.msg(source, "Your nickname '" + self.nick(source) + "' contains invalid characters. Allowed are the characters A-z and 0-9.")
		else:
			self.msg(source, "Syntax: HELLO <email> <email>")
