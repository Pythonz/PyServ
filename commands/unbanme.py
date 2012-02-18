import pyserv

class unbanme(pyserv.Command):
	help = "Unbans you from a channel where you are known"
	nauth = 1
	def onCommand(self, uid, args):
		from fnmatch import fnmatch
		arg = args.split()
		if len(arg) == 1:
			if self.chanexist(arg[0]):
				flag = self.getflag(uid, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
					for ban in self.query("select ban from banlist where channel = '%s'" % arg[0]):
						if fnmatch(self.hostmask(uid), str(ban[0])):
							self.mode(arg[0], "-b "+ban[0])
							self.query("delete from banlist where channel = '%s' and ban = '%s'" % (arg[0], ban[0]))
					self.msg(uid, "Done.")
				else: self.msg(uid, "Denied.")
			else: self.msg(uid, "Invalid channel: "+arg[0])
		else: self.msg(uid, "Syntax: UNBANME <#channel>")
