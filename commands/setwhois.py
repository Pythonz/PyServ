from pyserv import Command

class setwhois(Command):
	help = "Sets cool stuff in your whois"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) > 0:
			self.send(":{uid} SWHOIS {target} :{text}".format(uid=self.bot, target=source, text=' '.join(arg[0:])))
			self.msg(source, "Done.")
		else:
			self.send(":{uid} SWHOIS {target} :".format(uid=self.bot, target=source))
			self.msg(source, "Done.")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
