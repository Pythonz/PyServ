from pyserv import Command

class savhost(Command):
	help = "Manages vhosts of the users"
	oper = 1
	def onCommand(self, source, args):
		import _mysql
		arg = args.split()
		if len(arg) == 0:
			self.msg(source, "Account                   vHost")
			for data in self.query("select user,vhost from vhosts where active = '0'"):
				self.msg(source, "  %s %s %s" % (str(data["user"]), " "*int(20-len(data["user"])), str(data["vhost"])))
			self.msg(source, "End of list.")
		elif len(arg) == 1:
			if arg[0] == "?list":
				self.msg(source, "Account                 vHost")
				for data in self.query("select user,vhost from vhosts where active = '1'"):
					self.msg(source, "  {0} {1} {2}".format(data["user"], " "*int(20-len(data["user"])), data["vhost"]))
				self.msg(source, "End of list.")
			else:
				for data in self.query("select user,vhost from vhosts where active = '0' and user = '%s'" % arg[0]):
					self.query("update vhosts set active = '1' where user = '%s'" % str(data["user"]))
					self.query("insert into memo values ('%s', '%s', 'Your vHost %s has been activated.')" % (data["user"], self.bot_nick, data["vhost"]))
					for uid in self.sid(data["user"]):
						self.vhost(uid)
					self.memo(data["user"])
					self.msg(source, "Done.")
		elif len(arg) > 1:
			if arg[0] == "?set":
				if self.user(arg[1]):
					entry = False
					for data in self.query("select user,vhost from vhosts where vhost = '%s'" % arg[2]):
						user = data["user"]
						vhost = data["vhost"]
						entry = True
					if not entry:
						self.query("delete from vhosts where user = '%s'" % arg[1])
						self.query("insert into vhosts values ('%s', '%s', '1')" % (self.user(arg[1]), _mysql.escape_string(arg[2])))
						self.query("insert into memo values ('%s', '%s', '%s has been set as your vHost')" % (self.user(arg[1]), self.bot_nick, _mysql.escape_string(arg[2])))
						for uid in self.sid(arg[1]):
							self.vhost(uid)
						self.memo(arg[1])
						self.msg(source, "Done.")
					else:
						self.msg(source, "User %s is alreading using this vHost (%s)." % (user, vhost))
				else:
					self.msg(source, "Can't find user "+arg[1]+".")
			elif arg[0] == "?unset":
				if self.user(arg[1]):
					vhost = self.getvhost(arg[1])
					self.query("delete from vhosts where user = '%s'" % arg[1])
					self.query("insert into memo values ('%s', '%s', 'Your vHost %s has been deleted.')" % (self.user(arg[1]), self.bot_nick, vhost))
					for uid in self.sid(arg[1]):
						self.vhost(uid)
					self.memo(arg[1])
					self.msg(source, "Done.")
				else:
					self.msg(source, "Can't find user " + arg[1] + ".")
			else:
				for data in self.query("select * from vhosts where active = '0' and user = '%s'" % arg[0]):
					self.query("delete from vhosts where user = '%s'" % str(data["user"]))
					self.msg(source, "vHost for user %s has been rejected" % str(data["user"]))
					self.query("insert into memo values ('%s', '%s', 'Your vHost %s has been rejected. Reason: %s')" % (data["user"], self.bot_nick, data["vhost"], _mysql.escape_string(' '.join(arg[1:]))))
					self.memo(data[0])
		else: self.msg(source, "Syntax: SAVHOST [?list] [[?set] <user> [<reject-reason>]]")
