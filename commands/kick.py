from pyserv import Command

class kick(Command):
	help = "Kicks someone from the channel"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 2:
			if self.chanexist(arg[0]):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag =="o"or flag =="h":
					if arg[1].lower() != self.bot_nick.lower() and not self.isoper(self.uid(arg[1])):
						if self.onchan(arg[0],arg[1]):
							if self.chanflag("k", arg[0]):
								self.kick(arg[0], arg[1], self.nick(source))
							else:
								self.kick(arg[0], arg[1])
							self.msg(source, "Done.")
						else: self.msg(source, arg[1]+" is not on channel "+arg[0])
					else: self.msg(source, "Denied.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		elif len(arg) > 2:
			if self.chanexist(arg[0]):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag =="o"or flag =="h":
					if arg[1].lower() != self.bot_nick.lower() and not self.isoper(self.uid(arg[1])):
						if self.onchan(arg[0],arg[1]):
							if self.chanflag("k", arg[0]):
								self.kick(arg[0], arg[1], ' '.join(arg[2:]) + " (" + self.nick(source) + ")")
							else:
								self.kick(arg[0], arg[1], ' '.join(arg[2:]))
							self.msg(source, "Done.")
						else: self.msg(source, arg[1]+" is not on channel "+arg[0])
					else: self.msg(source, "Denied.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: KICK <#channel> <user> [,<user>] [reason]")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan + " " + args)
