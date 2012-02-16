import pyserv

class memo(pyserv.Command):
	help = "Send another user a memo"
	nauth = 1
	import _mysql
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) > 1:
			if arg[0].startswith("#"):
				user = arg[0][1:]
				sender = self.auth(source)
				message = _mysql.escape_string(' '.join(arg[1:]))
				entry = False
				for data in self.query("select name from users where name = '%s'" % user):
					user = data[0]
					entry = True
				if entry:
					self.query("insert into memo values ('%s', '%s', '%s')" % (user, sender, message))
					self.msg(source, "Done.")
					self.memo(user)
				else: self.msg(source, "Can't find user %s." % arg[0])
			else:
				user = self.auth(self.uid(arg[0]))
				sender = self.auth(source)
				message = _mysql.escape_string(' '.join(arg[1:]))
				entry = False
				for data in self.query("select name from users where name = '%s'" % user):
					user = data[0]
					entry = True
				if entry:
					self.query("insert into memo values ('%s', '%s', '%s')" % (user, sender, message))
					self.msg(source, "Done.")
					self.memo(user)
				else: self.msg(source, "Can't find user %s." % arg[0])
		else: self.msg(source, "Syntax: MEMO <user> <message>")
