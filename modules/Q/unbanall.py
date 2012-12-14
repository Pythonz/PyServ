from pyserv import Command

class unbanall(Command):
	help = "Removes all bans from your channel"
	nauth = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 1:
			if self.chanexist(arg[0]):
				flag = self.getflag(uid, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a":
					for ban in self.query("select ban from banlist where channel = '%s'" % arg[0]):
						self.mode(arg[0], "-b "+ban["ban"])
						self.msg(uid, " - removed '"+ban["ban"]+"'")
						
					self.query("delete from banlist where channel = '%s'" % arg[0])
					self.msg(uid, "Done.")
				else:
					self.msg(uid, "Denied.")
			else:
				self.msg(uid, "Invalid channel: "+arg[0])
		else:
			self.msg(uid, "Syntax: UNBANALL <#channel>")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan)
