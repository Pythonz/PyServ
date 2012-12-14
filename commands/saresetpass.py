from pyserv import Command
from time import time
from _mysql import escape_string

class saresetpass(Command):
	help = "Reset your lost password"
	oper = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 1:
			entry = False
			
			for data in self.query("select name,pass,email,suspended from users where name = '%s'" % (escape_string(arg[0]))):
				entry = True
				
				if data["suspended"] == "0":
					newpw = str(hash(str(time()) + data["name"] + data["pass"] + data["email"]))
					self.query("update users set pass = '%s' where name = '%s' and email = '%s'" % (self.encode(newpw), escape_string(data["name"]), escape_string(data["email"])))
					self.msg(uid, "The new password of the user {0} is {1}. He/She should change it as soon as possible!".format(data["name"], newpw))
				else:
					self.msg(uid, "The account have been banned from " + self.services_description + ". Reason: " + data["suspended"])
					
			if not entry:
				self.msg(uid, "Can't find user " + arg[0] + ".")
		else:
			self.msg(uid, "Syntax: RESETPASS <account>")
