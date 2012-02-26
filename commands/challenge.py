from pyserv import Command, config

class challenge(Command):
	help = "Request a challenge at " + config.get("BOT", "nick") + "@" + config.get("SERVICES", "name")
	def onCommand(self, uid, args):
		if self.auth(uid) == 0:
			import hmac
			import time
			import _mysql
			entry = False
			for data in self.query("select challenge from challenges where hostmask = '%s'" % _mysql.escape_string(self.hostmask(uid)[0])):
				entry = True
				ChallengeCode = data["challenge"]
				self.msg(uid, "CHALLENGE {0} HMAC-MD5 HMAC-SHA-1 HMAC-SHA-256 HMAC-SHA-512".format(ChallengeCode))
			if not entry:
				ChallengeCode = hmac.new(str(time.time()), self.hostmask(uid)[0]).hexdigest()
				self.msg(uid, "CHALLENGE {0} HMAC-MD5 HMAC-SHA-1 HMAC-SHA-256 HMAC-SHA-512".format(ChallengeCode))
				self.query("insert into challenges values ('%s', '%s')" % (_mysql.escape_string(self.hostmask(uid)[0]), ChallengeCode))
		else:
			self.msg(uid, "CHALLENGE is not available once you have authed.")
