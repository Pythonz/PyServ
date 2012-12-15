from pyserv import Command

class banlist(Command):
	help = "Sends you the banlist of your channel"
	nauth = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 1:
			if self.chanexist(arg[0]):
				flag = self.getflag(uid, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
					self.msg(uid, "Banlist for "+arg[0])
					
					for ban in self.query("select ban from banlist where channel = '%s' order by id" % arg[0]):
						self.msg(uid, "  "+ban["ban"])
						
					self.msg(uid, "End of list.")
				else:
					self.msg(uid, "Denied.")
			else:
				self.msg(uid, "Invalid channel: "+arg[0])
		else:
			self.msg(uid, "Syntax: BANLIST <#channel>")

	def onFantasy(self, uid, chan, args):
		flag = self.getflag(uid, chan)
		
		if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
			self.onCommand(uid, chan + " " + args)
