from pyserv import Command

class ban(Command):
	help = "Bans somebody from your channel"
	nauth = 1

	def onCommand(self, uid, args):
		from fnmatch import fnmatch
		
		try:
			arg = args.split()
			
			if len(arg) == 2:
				if self.chanexist(arg[0]):
					flag = self.getflag(uid, arg[0])
					
					if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
						if fnmatch(arg[1], "*!*@*") and arg[1] != "*!*@*":
							entry = False
							
							for data in self.query("select * from banlist where ban = '%s' and channel='%s'" % (arg[1], arg[0])):
								entry = True
								
							if not entry:
								self.query("insert into banlist (`channel`, `ban`) values ('%s', '%s')" % (arg[0], arg[1]))
								self.msg(uid, "Done.")
								self.enforceban(arg[0], arg[1])
							else:
								self.msg(uid, arg[1]+" is already in the banlist of "+arg[0])
						else:
							uentry = False
							
							for user in self.userlist(arg[0]):
								if self.nick(user).lower() == arg[1].lower():
									uentry = True
									entry = False
									
									if self.gethost(user) == self.getip(user):
										if self.userflag(user, "x"):
											ban = "*!*@" + user + ".users." + self.getservicedomain()
										elif self.getip(user).find(":") != -1:
											ban = "*!*"+self.userhost(user).split("@")[0]+"@"+':'.join(self.getip(user).split(":")[:-2])+":*"
										else:
											ban = "*!*"+self.userhost(user).split("@")[0]+"@"+'.'.join(self.getip(user).split(".")[:-1])+".*"
									else:
										ban = "*!*"+self.userhost(user).split("@")[0]+"@*."+'.'.join(self.gethost(user).split(".")[1:])
										
									for data in self.query("select * from banlist where ban = '%s' and channel='%s'" % (ban, arg[0])):
										entry = True
										
									if not entry:
										self.query("insert into banlist (`channel`, `ban`) values ('%s', '%s')" % (arg[0], ban))
										self.msg(uid, "Done.")
										self.enforceban(arg[0], ban)
									else:
										self.msg(uid, ban+" is already in the banlist of "+arg[0])
										
							if not uentry:
								self.msg(uid, "Can't find user "+arg[1]+" on "+arg[0]+".")
					else:
						self.msg(uid, "Denied.")
				else:
					self.msg(uid, "Invalid channel: "+arg[0])
			else:
				self.msg(uid, "Syntax: BAN <#channel> <hostmask>")
		except pyserv.error,e:
			pass

	def onFantasy(self, uid, chan, args):
		flag = self.getflag(uid, chan)
		
		if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
			self.onCommand(uid, chan + " " + args)
