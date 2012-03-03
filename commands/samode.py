from pyserv import Command

class samode(Command):
	help = "Change modes on a channel where you have no rights"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) > 1:
			if arg[0].startswith("#"):
				self.mode(arg[0], ' '.join(arg[1:]))
				self.msg(uid, "Done.")
			else:
				self.msg(uid, "Invalid channel: " + arg[0])
		else:
			self.msg(uid, "Syntax: SAMODE <#channel> <modes>")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan + " " + args)
