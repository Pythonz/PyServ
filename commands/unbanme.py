from pyserv import Command

class unbanme(Command):
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
						if self.gateway(uid):
							crypthost = ''.join([char for char in self.encode(uid) if char.isalnum()])+".gateway."+'.'.join(self.services_name.split(".")[-2:])
							if fnmatch(self.nick(uid)+"!"+self.userhost(uid).split("@")[0]+"@"+crypthost, ban["ban"]):
								self.mode(arg[0], "-b "+ban["ban"])
								self.msg(uid, " - removed '"+ban["ban"]+"'")
								self.query("delete from banlist where channel = '%s' and ban = '%s'" % (arg[0], ban["ban"]))
						for hostmask in self.hostmask(uid):
							if fnmatch(hostmask, str(ban["ban"])):
								self.mode(arg[0], "-b "+ban["ban"])
								self.msg(uid, " - removed '"+ban["ban"]+"'")
								self.query("delete from banlist where channel = '%s' and ban = '%s'" % (arg[0], ban["ban"]))
					self.msg(uid, "Done.")
				else: self.msg(uid, "Denied.")
			else: self.msg(uid, "Invalid channel: "+arg[0])
		else: self.msg(uid, "Syntax: UNBANME <#channel>")
