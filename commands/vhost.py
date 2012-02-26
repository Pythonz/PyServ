from pyserv import Command

class vhost(Command):
	help = "Request a vHost for your account"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].find(".") == -1:
				self.msg(source, "Invalid vhost. Where's the dot?")
			elif arg[0][-2] == "." or arg[0][-1] == ".":
				self.msg(source, "Domain ending is too short.")
			elif arg[0].find("@") != -1 and len(arg[0].split("@")[0]) < 3:
				self.msg(source, "vIdent too short.")
			elif arg[0].find("@") != -1 and len(arg[0].split("@")[1]) < 6:
				self.msg(source, "vHost too short.")
			elif arg[0].find("@") != -1 and arg[0].split("@")[0].find(".") != -1:
				self.msg(source, "No dots allowed in vIdent.")
			elif arg[0].find("@") != -1 and arg[0].split("@")[1].find(".") == -1:
				self.msg(source, "Thats no vHost, the DOT is missing.")
			elif len(arg[0]) < 6:
				self.msg(source, "Your vhost is too short.")
			else:
				entry = False
				vhost = arg[0]
				if vhost.find("@") != -1:
					vhost = vhost.split("@")[0]
				for data in self.query("select user from vhosts where vhost = '%s' and user != '%s'" % (vhost, self.auth(source))):
					user = data["user"]
					entry = True
				if not entry:
					self.query("delete from vhosts where user = '%s'" % self.auth(source))
					self.query("insert into vhosts values ('%s','%s','0')" % (self.auth(source), arg[0]))
					self.msg(source, "Your new vhost %s has been requested" % arg[0])
					for data in self.query("select host,username from online where uid = '%s'" % source):
						if not self.isbot(source):
							self.send(":%s CHGIDENT %s %s" % (self.bot, source, data["username"]))
							self.send(":%s CHGHOST %s %s" % (self.bot, source, data["host"]))
						else:
							self.send(":%s CHGIDENT %s %s" % (self.bot, source, data["username"]))
							crypthost = ''.join([char for char in self.encode(source) if char.isalnum()]).lower()
							self.send(":%s CHGHOST %s %s.bots.gateway.%s" % (self.bot, source, crypthost, '.'.join(self.services_name.split(".")[-2:])))
					for data in self.query("select uid from opers"):
						self.msg(data["uid"], "vHost request received from %s" % self.auth(source))
				else:
					self.msg(source, "%s is already using this vHost." % user)
		elif len(arg) == 0:
			self.query("delete from vhosts where user = '%s'" % self.auth(source))
			self.msg(source, "Done.")
			for data in self.query("select host,username from online where uid = '%s'" % source):
				if not self.isbot(source):
					self.send(":%s CHGIDENT %s %s" % (self.bot, source, data["username"]))
					self.send(":%s CHGHOST %s %s" % (self.bot, source, data["host"]))
				else:
					self.send(":%s CHGIDENT %s %s" % (self.bot, source, data["username"]))
					crypthost = ''.join([char for char in self.encode(source) if char.isalnum()]).lower()
					self.send(":%s CHGHOST %s %s.bots.gateway.%s" % (self.bot, source, crypthost, '.'.join(self.services_name.split(".")[-2:])))
		else:
			self.msg(source, "Syntax: VHOST <vhost>")
