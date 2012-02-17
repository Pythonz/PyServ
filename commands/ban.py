import pyserv

class ban(pyserv.Command):
	help = "Bans somebody from your channel"
	nauth = 1
	def onCommand(self, uid, args):
		from fnmatch import fnmatch
		try:
			arg = args.split()
			if len(arg) == "2":
				if arg[0].startswith("#"):
					flag = self.getflag(uid, arg[0])
					if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
						if fnmatch(arg[1], "*!*@*"):
							entry = False
							for data in self.query("select * from banlist where ban = '%s' and channel='%s'" % (arg[1], arg[0])):
								entry = True
							if not entry:
								self.query("insert into banlist values ('%s', '%s')" % (arg[0], arg[1]))
								self.msg(uid, "Done.")
								self.enforceban(arg[0], arg[1])
							else: self.msg(uid, arg[1]+" is already in the banlist of "+arg[0])
						else: self.msg(uid, "Invalid hostmask: "+arg[1])
					else: self.msg(uid, "Denied.")
				else: self.msg(uid, "Invalid channel: "+arg[0])
			else: self.msg(uid, "Syntax: BAN <#channel> <hostmask>")
		except pyserv.error,e: pass
		
