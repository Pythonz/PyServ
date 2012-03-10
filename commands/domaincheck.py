from pyserv import Command

class domaincheck(Command):
	help = "Shows you a domain lookup result"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			from subprocess import Popen, PIPE
			from urllib2 import urlopen
			self.msg(uid, "Check domain: "+arg[0])
			domain = Popen(["whois", arg[0]], stdout=PIPE).stdout.read().splitlines()
			for line in domain:
				if line != "" and line[0] != "%":
					if line[0] == "[" and line[-1] == "]":
						self.msg(uid)
					self.msg(uid, line)
		else: self.msg(uid, "Syntax: DOMAINCHECK <domain>")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
