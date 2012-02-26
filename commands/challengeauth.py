from pyserv import Command, config

class challengeauth(Command):
	help = "Authes you with your CHALLENGE request at " + config.get("BOT", "nick") + "@" + config.get("SERVICES", "name")
	def onCommand(self, uid, args):
		if self.auth(uid) == 0:
			arg = args.split()
			if len(arg) == 3:
				import hashlib
				import hmac
				import _mysql
				correct = False
				user = arg[0]
				resp = arg[1]
				alg = arg[2]
				entry = False
				for challenges in self.query("select challenge from challenges where hostmask = '%s'" % _mysql.escape_string(self.hostmask(uid)[0])):
					entry = True
					challenge = challenges["challenge"]
					self.query("delete from challenges where hostmask = '%s'" % _mysql.escape_string(self.hostmask(uid)[0]))
					for data in self.query("select name,pass from users where name = '%s'" % user):
						if alg.lower() == "hmac-md5" and user == data["name"]:
							hash_pass = hashlib.md5(self.decode(data["pass"])).hexdigest()
							key = hashlib.md5(data["name"]+":"+hash_pass).hexdigest()
							response = hmac.new(challenge, key, digestmod=hashlib.md5).hexdigest()
							if response == resp:
								correct = True
						if alg.lower() == "hmac-sha-1" and user == data["name"]:
							hash_pass = hashlib.sha1(self.decode(data["pass"])).hexdigest()
							key = hashlib.sha1(data["name"]+":"+hash_pass).hexdigest()
							response = hmac.new(challenge, key, digestmod=hashlib.sha1).hexdigest()
							if response == resp:
								correct = True
						if alg.lower() == "hmac-sha-256" and user == data["name"]:
							hash_pass = hashlib.sha256(self.decode(data["pass"])).hexdigest()
							key = hashlib.sha256(data["name"]+":"+hash_pass).hexdigest()
							response = hmac.new(challenge, key, digestmod=hashlib.sha256).hexdigest()
							if response == resp:
								correct = True
						if alg.lower() == "hmac-sha-512" and user == data["name"]:
							hash_pass = hashlib.sha512(self.decode(data["pass"])).hexdigest()
							key = hashlib.sha512(data["name"]+":"+hash_pass).hexdigest()
							response = hmac.new(challenge, key, digestmod=hashlib.sha512).hexdigest()
							if response == resp:
								correct = True
					if correct:
						for temp in self.query("select nick from temp_nick where user = '%s'" % user):
							self.msg(temp["nick"], "Warning: %s (%s) authed with your password." % (self.nick(uid), self.userhost(uid)))
						self.query("insert into temp_nick values ('%s','%s')" % (uid, user))
						self.msg(uid, "You are now logged in as %s" % user)
						self.msg(uid, "Remember: NO-ONE from %s will ever ask for your password.  NEVER send your password to ANYONE except Q@%s." % (self.services_description, self.services_name))
						self.meta(uid, "accountname", user)
						self.usermodes(uid)
						self.vhost(uid)
						self.flag(uid)
						self.autojoin(uid)
						self.memo(user)
					else:
						self.msg(uid, "CHALLENGEAUTH failed. CHALLENGEAUTH is case-sensitive.")
				if not entry:
					self.msg(uid, "You have to request a CHALLENGE first.")
			else:
				self.msg(uid, "Syntax: <username> <response> <hmac algorithm>")
		else:
			self.msg(uid, "CHALLENGEAUTH is not available once you have authed.")
