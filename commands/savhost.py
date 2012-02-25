from pyserv import Command

class savhost(Command):
	help = "Manages vhosts of the users"
	oper = 1
	def onCommand(self, source, args):
		import _mysql
		arg = args.split()
		if len(arg) == 0:
			self.msg(source, "Waiting:")
			self.msg(source, "  Account               vHost")
			for data in self.query("select user,vhost from vhosts where active = '0'"):
				self.msg(source, "%s %s %s" % (str(data["user"]), " "*int(13-len(data["user"])), str(data["vhost"])))
		elif len(arg) == 1:
			for data in self.query("select user,vhost from vhosts where active = '0' and user = '%s'" % arg[0]):
				self.query("update vhosts set active = '1' where user = '%s'" % str(data["user"]))
				self.query("insert into memo values ('%s', 'Q', 'Your vHost %s has been activated.')" % (data["user"], data["vhost"]))
				for uid in self.sid(data["user"]):
					self.vhost(uid)
					self.memo(data["user"])
				self.msg(source, "Done.")
		elif len(arg) > 1:
			for data in self.query("select * from vhosts where active = '0' and user = '%s'" % arg[0]):
				self.query("delete from vhosts where user = '%s'" % str(data["user"]))
				self.msg(source, "vHost for user %s has been rejected" % str(data["user"]))
				self.query("insert into memo values ('%s', 'Q', 'Your vHost %s has been rejected. Reason: %s')" % (data["user"], data["vhost"], _mysql.escape_string(' '.join(arg[1:]))))
				self.memo(data[0])
		else: self.msg(source, "Syntax: SAVHOST [<user> [<reject-reason>]]")
