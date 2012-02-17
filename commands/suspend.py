import pyserv

class suspend(pyserv.Command):
	help = "Suspends a channel"
	oper = 1
	def onCommand(self, uid, args):
		import _mysql
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				if self.suspended(arg[0]):
					self.query("delete from suspended where channel = '%s'" % arg[0])
					self.msg(uid, "Unsuspended.")
				else: self.msg(uid, arg[0]+" is not suspended.")
			elif arg[0] == "?": self.msg(uid, "Syntax: SUSPEND <#channel> [<reason>]")
			else: self.msg(uid, "Invalid channel: "+arg[0])
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				if not self.suspended(arg[0]):
					self.query("insert into suspended values ('%s', '%s')" % (arg[0], _mysql.escape_string(' '.join(arg[1:]))))
					for user in self.userlist(arg[0]):
						if not self.isoper(user):
							self.gline(user, "Suspended "+arg[1]+": "+' '.join(arg[1]))
				else:
					self.query("update suspended set reason = '%s' where channel = '%s'" % (_mysql.escape_string(' '.join(arg[1:])), arg[0]))
					for user in self.userlist(arg[0]):
						if not self.isoper(user):
							self.gline(user, "Suspended "+arg[1]+": "+' '.join(arg[1]))
				self.msg(uid, "Suspended.")
			else: self.msg(uid, "Invalid channel: "+arg[0])
		else:
			for data in self.query("select * from suspended"):
				self.msg(uid, "Channel: {0} {1} Reason: {2}".format(data[0], " "*int(23-len(data[0])), data[1]))
