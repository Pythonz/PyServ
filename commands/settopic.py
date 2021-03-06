from pyserv import Command

class settopic(Command):
	help = "Sets topic for your channel"
	nauth = 1

	def onCommand(self, source, args):
		import _mysql
		arg = args.split()
		
		if len(arg) > 1:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "q" or self.getflag(source, arg[0]) == "a":
					self.query("update channelinfo set topic = '{0}' where name = '{1}'".format(_mysql.escape_string(' '.join(arg[1:])), arg[0]))
					self.send(":{0} TOPIC {1} :{2}".format(self.bot, arg[0], ' '.join(arg[1:])))
					
					if self.chanflag("l", arg[0]):
						self.log("Q", "topic", arg[0], ":"+' '.join(arg[1:]))
						
					self.msg(source, "Done.")
				else:
					self.msg(source, "No permission")
			else:
				self.msg(source, "Invalid channel '{0}'".format(arg[0]))
		else:
			self.msg(source, "Syntax: SETTOPIC <#channel> <topic>")

	def onFantasy(self, uid, chan, args):
		flag = self.getflag(uid, chan)
		
		if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
			self.onCommand(uid, chan + " " + args)
