import pyserv

class setwhois(pyserv.Command):
	help = "Sets cool stuff in your whois"
	def onCommand(self, source, args):
		arg = args.split()
		if self.auth(source):
			if len(arg) > 1:
				self.send(":{uid} SWHOIS {target} :{text}".format(uid=self.bot, target=source, text=' '.join(arg[1:])))
				self.msg(source, "Done.")
			else:
				self.send(":{uid} SWHOIS {target} :".format(uid=self.bot, target=source))
				self.msg(source, "Done.")
		else: self.unknown(source)
