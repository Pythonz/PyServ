from pyserv import Command

class deowner(Command):
	help = "Removes your owner (+q) flag"
	nauth = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) == 1:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "q":
					self.mode(arg[0], "-qo {0} {0}".format(source))
					self.msg(source, "Done.")
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		else:
			self.msg(source, "Syntax: DEOWNER <#channel>")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan)
