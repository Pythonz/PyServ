from pyserv import Command

class domaincheck(Command):
	help = "Shows you a domain lookup result"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			from pywhois import whois
			self.msg(uid, "Check domain: "+arg[0])
			domain = str(whois(arg[0])).splitlines()
			for line in domain:
				self.msg(uid, line)
			self.msg(uid, "End of check.")
		else: self.msg(uid, "Syntax: DOMAINCHECK <domain>")
