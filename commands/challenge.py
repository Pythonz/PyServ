from pyserv import Command

class challenge(Command):
	help = "Request a challenge"
	def onCommand(self, uid, args):
		if self.auth(uid) == 0:
			import hmac
			self.msg(uid, "CHALLENGE {0} HMAC-MD5 HMAC-SHA-1 HMAC-SHA-256 HMAC-SHA-512".format(hmac.new(self.hostmask(uid)).hexdigest()))
		else:
			self.msg(uid, "CHALLENGE is not available once you have authed.")
