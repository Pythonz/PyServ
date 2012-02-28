from pyserv import Command

class requestpass(Command):
	help = "Request your lost password"
	def onCommand(self, uid, args):
		if self.auth(uid) == 0:
			arg = args.split()
			if len(arg) == 1:
				entry = False
				for data in self.query("select name,pass,email,suspended from users where name = '%s'" % arg[0]):
					entry = True
					if data["suspended"] == "0":
						self.mail(data["email"], "From: %s <%s>\nTo: %s <%s>\nSubject: Lost password\nThis is an automated message, do not respond to this email!\n\nAccount: %s\nPassword: %s" % (self.services_description, self.email, data["name"], data["email"], data["name"], self.decode(data["pass"])))
						self.msg(uid, "I've sent an email with your lost password to %s." % data["email"])
					else:
						self.msg(source, "Your account have been banned from " + self.services_description + ". Reason: " + data["suspended"])
				if not entry:
					self.msg(uid, "Can't find user " + arg[0])
			else:
				self.msg(uid, "Syntax: REQUESTPASS <account>")
		else:
			self.msg(uid, "REQUESTPASS is not available once you have authed.")
