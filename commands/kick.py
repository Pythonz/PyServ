import pyserv

class kick(pyserv.Command):
	help = "Kicks someone from the channel"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 2:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag =="o"or flag =="h":
					if arg[1].lower() != "q" and not self.isoper(self.uid(arg[1])):
						self.send(":{0} KICK {1} {2} :{2}".format(self.bot, arg[0], arg[1]))
						self.msg(source, "Done.")
					else: self.msg(source, "Denied.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		elif len(arg) > 2:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag =="o"or flag =="h":
					if arg[1].lower() != "q" and not self.isoper(self.uid(arg[1])):
						self.send(":{0} KICK {1} {2} :{3}".format(self.bot, arg[0], arg[1], ' '.join(arg[2:])))
						self.msg(source, "Done.")
					else: self.msg(source, "Denied.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: KICK <#channel> <user> [,<user>] [reason]")
