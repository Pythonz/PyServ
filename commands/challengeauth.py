from pyserv import Command

class challengeauth(Command):
	help = "Authes you with your CHALLENGE request"
	def onCommand(self, uid, args):
		if self.auth(uid) == 0:
			arg = args.split()
			if len(arg) == 3:
				import hashlib
				import hmac
				correct = False
				user = arg[0]
				resp = arg[1]
				alg = arg[2]
				challenge = hmac.new(self.hostmask(uid)).hexdigest()
				for data in self.query("select pass from users where name = '%s'" % user):
					if alg.lower() == "hmac-md5":
						hash_pass = hashlib.md5(self.decode(data["pass"])).hexdigest()
						key = hashlib.md5(user+":"+hash_pass).hexdigest()
						response = hmac.new(challenge, key)
						if response == resp:
							correct = True
					if alg.lower() == "hmac-sha-1":
						hash_pass = hashlib.sha1(self.decode(data["pass"])).hexdigest()
						key = hashlib.sha1(user+":"+hash_pass).hexdigest()
						response = hmac.new(challenge, key)
						if response == resp:
							correct = True
					if alg.lower() == "hmac-sha-256":
						hash_pass = hashlib.sha256(self.decode(data["pass"])).hexdigest()
						key = hashlib.sha256(user+":"+hash_pass).hexdigest()
						response = hmac.new(challenge, key)
						if response == resp:
							correct = True
					if alg.lower() == "hmac-sha-512":
						hash_pass = hashlib.sha512(self.decode(data["pass"])).hexdigest()
						key = hashlib.sha512(user+":"+hash_pass).hexdigest()
						response = hmac.new(challenge, key)
						if response == resp:
							correct = True
					if correct:
						for temp in self.query("select nick from temp_nick where user = '%s'" % user):
							self.msg(temp["nick"], "Warning: %s (%s) authed with your password." % (self.nick(uid), self.userhost(uid)))
						self.query("insert into temp_nick values ('%s','%s')" % (uid, user))
						self.msg(uid, "You are now logged in as %s" % user)
						self.msg(uid, "Remember: NO-ONE from %s will ever ask for your password.  NEVER send your password to ANYONE except Q@%s." % (self.services_description, self.services_name))
						self.meta(uid, "accountname", user)
						self.vhost(uid)
						self.flag(uid)
						self.autojoin(uid)
						self.memo(user)
			else:
				self.msg(uid, "Syntax: <username> <response> <hmac algorithm>")
		else:
			self.msg(uid, "CHALLENGEAUTH is not available once you have authed.")
