from pyserv import Command

class domaincheck(Command):
	help = "Shows you a domain lookup result"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			from pywhois import whois
			from urllib2 import urlopen
			self.msg(uid, "Check domain: "+arg[0])
			if self.scanport(arg[0], 80) or self.scanport(arg[0], 443):
				if self.scanport(arg[0], 80):
					prefix = "http"
				else:
					prefix = "https"
				site = urlopen(prefix + "://" + arg[0])
				content = site.read()
				site.close()
				title = content.split("<title>")[1].split("</title>")[0]
				self.msg(uid, "Title: " + title)
			domain = str(whois(arg[0])).splitlines()
			for line in domain:
				self.msg(uid, line)
			self.msg(uid, "End of check.")
		else: self.msg(uid, "Syntax: DOMAINCHECK <domain>")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
