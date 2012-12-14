from pyserv import Command

class suspend(Command):
	help = "Suspends a channel"
	oper = 1

	def onCommand(self, uid, args):
		import _mysql
		arg = args.split()
		if len(arg) > 1:
			channel = _mysql.escape_string(arg[1])
		if len(arg) > 2:
			reason = _mysql.escape_string(' '.join(arg[2:]))
		
		if len(arg) == 2 && arg[0].lower() == "remove":
			if arg[1].startswith("#"):
				if self.suspended(channel):
					self.query("delete from suspended where channel = '%s'" % channel)
					self.msg(uid, "Unsuspended.")
				else:
					self.msg(uid, arg[1]+" is not suspended.")
			else:
				self.msg(uid, "Invalid channel: "+arg[1])
		elif len(arg) > 2 && arg[0].lower() == "set":
			if arg[1].startswith("#"):
				if not self.suspended(channel):
					self.query("insert into suspended (`channel`, `reason`) values ('%s', '%s')" % (channel, reason))
					
					if self.chanexist(channel):
						self.query("delete from channels where channel = '{0}'".format(channel))
						self.query("delete from channelinfo where name = '{0}'".format(channel))
						self.query("delete from banlist where channel = '{0}'".format(channel))
						self.send(":{0} PART {1} :Channel {1} has been suspended.".format(self.bot, arg[1]))
						
					for user in self.userlist(channel):
						if not self.isoper(user):
							self.kick(arg[1], user, "Suspended: "+' '.join(arg[2:]))
						else:
							self.msg(arg[1], "This channel is suspended: "+' '.join(arg[2:]))
				else:
					self.query("update suspended set reason = '%s' where channel = '%s'" % (reason, channel))
					
					for user in self.userlist(channel):
						if not self.isoper(user):
							self.kick(arg[1], user, "Suspended: "+' '.join(arg[2:]))
						else:
							self.msg(arg[1], "This channel is suspended: "+' '.join(arg[2:]))
							
				self.msg(uid, "Suspended.")
			else:
				self.msg(uid, "Invalid channel: "+arg[1])
		elif len(arg) == 2 && arg[0].lower() == "list":
			for data in self.query("select * from suspended"):
				self.msg(uid, "Channel: {0} {1} Reason: {2}".format(data["channel"], " "*int(23-len(data["channel"])), data["reason"]))
		else:
			self.msg(uid, "Syntax: SUSPEND <list/set/remove> <#channel> [<reason>]")
	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, channel + " " + args)
