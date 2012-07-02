from pyserv import Command

class email(Command):
	help = "Changes your account email"
	nauth = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 1:
			if arg[0].find("@") != -1:
				if len(arg[0].split("@")[0]) != 0:
					if arg[0].split("@")[1].find(".") != -1:
						if arg[0].split("@")[1][-1] != "." and arg[0].split("@")[1][-2] != "." and arg[0].split("@")[1][0] != ".":
							entry = False
							
							for data in self.query("select * from users where email = '%s'" % arg[0]):
								entry = True
								
							if not entry:
								self.query("update users set email = '%s' where name = '%s'" % (arg[0], self.auth(uid)))
								self.mail(arg[0], "From: {server} <{servermail}>\nTo: {user} <{usermail}>\nSubject: Email verification\nYour Email address has been changed to {usermail} successfully.".format(server=self.services_description, servermail=self.email, user=self.auth(uid), usermail=arg[0]))
								self.msg(uid, "Done.")
							else:
								self.msg(uid, "Email address already in use.")
						else:
							self.msg(uid, "Invalid email: "+arg[0])
					else:
						self.msg(uid, "Invalid email: "+arg[0])
				else:
					self.msg(uid, "Invalid email: "+arg[0])
			else:
				self.msg(uid, "Invalid email: "+arg[0])
		else:
			self.msg(uid, "Syntax: EMAIL <email>")
