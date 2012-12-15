from pyserv import Command
import _mysql

class memo(Command):
	help = "Send another user a memo"
	nauth = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) > 1:
			if arg[0].startswith("#"):
				user = arg[0][1:]
				
				if self.user(user):
					sender = self.auth(source)
					message = _mysql.escape_string(' '.join(arg[1:]))
					self.query("insert into memo (`user`, `source`, `message`) values ('%s', '%s', '%s')" % (user, sender, message))
					self.msg(source, "Done.")
					self.memo(user)
				else:
					self.msg(source, "Can't find user %s." % arg[0])
			else:
				user = self.auth(self.uid(arg[0]))
				
				if self.user(user):
					sender = self.auth(source)
					message = _mysql.escape_string(' '.join(arg[1:]))
					self.query("insert into memo (`user`, `source`, `message`) values ('%s', '%s', '%s')" % (user, sender, message))
					self.msg(source, "Done.")
					self.memo(user)
				else:
					self.msg(source, "Can't find user %s." % arg[0])
		else:
			self.msg(source, "Syntax: MEMO <user> <message>")
