from pyserv import Command

class sakick(Command):
	help = "Kicks someone from the channel"
	oper = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) == 2:
			if arg[0].startswith("#"):
				if arg[1].lower() != self.bot_nick.lower() and not self.isoper(self.uid(arg[1])):
					if self.onchan(arg[0],arg[1]):
						self.kick(arg[0], arg[1])
						self.msg(source, "Done.")
					else:
						self.msg(source, arg[1]+" is not on channel "+arg[0])
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		elif len(arg) > 2:
			if arg[0].startswith("#"):
				if arg[1].lower() != self.bot_nick.lower() and not self.isoper(self.uid(arg[1])):
					if self.onchan(arg[0],arg[1]):
						self.kick(arg[0], arg[1], ' '.join(arg[2:]))
						self.msg(source, "Done.")
					else:
						self.msg(source, arg[1]+" is not on channel "+arg[0])
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		else:
			self.msg(source, "Syntax: KICK <#channel> <user> [,<user>] [reason]")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan + " " + args)
