from pyserv import Command
from time import time
from _mysql import escape_string

class resetpass(Command):
	help = "Reset your lost password"

	def onCommand(self, uid, args):
		if self.auth(uid) == 0:
			arg = args.split()
			
			if len(arg) == 2:
				entry = False
				
				for data in self.query("select name,pass,email,suspended from users where name = '%s' and email = '%s'" % (arg[0], arg[1])):
					entry = True
					
					if data["suspended"] == "0":
						newpw = str(hash(str(time()) + data["name"] + data["pass"] + data["email"]))
						self.query("update users set pass = '%s' where user = '%s' and email = '%s'" % (self.encode(newpw), escape_string(arg[0]), escape_string(arg[1])))
						self.mail(data["email"], "From: %s <%s>\nTo: %s <%s>\nSubject: Password reset\nThis is an automated message, do not respond to this email!\n\nAccount: %s\nPassword: %s" % (self.services_description, self.email, data["name"], data["email"], data["name"], newpw))
						self.msg(uid, "I've sent an email with your lost password to %s." % data["email"])
					else:
						self.msg(uid, "Your account have been banned from " + self.services_description + ". Reason: " + data["suspended"])
						
				if not entry:
					self.msg(uid, "Can't find user " + arg[0] + " with email " + arg[1] + ".")
			else:
				self.msg(uid, "Syntax: RESETPASS <account> <email>")
		else:
			self.msg(uid, "RESETPASS is not available once you have authed.")
