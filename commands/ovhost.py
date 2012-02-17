import pyserv

class ovhost(pyserv.Command):
	help = "Manages vhosts of the users"
	oper = 1
	def onCommand(self, source, args):
		import _mysql
		arg = args.split()
		if len(arg) == 1:
			if arg[0].lower() == "list":
				for data in self.query("select user,vhost from vhosts where active = '0'"):
					self.msg(source, "User: %s\t|\tRequested vHost: %s" % (str(data[0]), str(data[1])))
			else: self.msg(source, "Syntax: OVHOST <list>/<activate>/<reject> [<user>] [reason]")
		elif len(arg) == 2:
			if arg[0].lower() == "activate":
				for data in self.query("select user,vhost from vhosts where active = '0' and user = '%s'" % arg[1]):
					self.query("update vhosts set active = '1' where user = '%s'" % str(data[0]))
					self.query("insert into memo values ('%s', 'Q', 'Your vHost\2 %s\2 has been activated.')" % (data[0], data[1]))
					for uid in self.sid(data[0]):
						self.vhost(uid)
						self.memo(data[0])
					self.msg(source, "Done.")
			else: self.msg(source, "Syntax: OVHOST <list>/<activate>/<reject> [<user>] [reason]")
		elif len(arg) > 2:
			if arg[0].lower() == "reject":
				for data in self.query("select * from vhosts where active = '0' and user = '%s'" % arg[1]):
					self.query("delete from vhosts where user = '%s'" % str(data[0]))
					self.msg(source, "vHost for user\2 %s\2 has been rejected" % str(data[0]))
					self.query("insert into memo values ('%s', 'Q', 'Your vHost\2 %s\2 has been rejected. Reason: %s')" % (data[0], data[1], _mysql.escape_string(' '.join(arg[2:]))))
					self.memo(data[0])
			else: self.msg(source, "Syntax: OVHOST <list>/<activate>/<reject> [<user>] [reason]")
		else: self.msg(source, "Syntax: OVHOST <list>/<activate>/<reject> [<user>] [reason]")
