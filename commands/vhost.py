import pyserv

class vhost(pyserv.Command):
	help = "Request a vHost for your account"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if len(arg[0]) < 5:
				self.msg(source, "Your vhost is too short.")
			elif arg[0].find(".") == -1:
				self.msg(source, "Invalid vhost. Where's the dot?")
			elif arg[0][-2] == "." or arg[0][-1] == ".":
				self.msg(source, "Domain ending is too short.")
			else:
				self.query("delete from vhosts where user = '%s'" % self.auth(source))
				self.query("insert into vhosts values ('%s','%s','0')" % (self.auth(source), arg[0]))
				self.msg(source, "Your new vhost\2 %s\2 has been requested" % arg[0])
				for data in self.query("select host,username from online where uid = '%s'" % source):
					self.send(":%s CHGIDENT %s %s" % (self.bot, source, data[1]))
					self.send(":%s CHGHOST %s %s" % (self.bot, source, data[0]))
				for data in self.query("select uid from opers"):
					self.msg(data[0], "vHost request received from\2 %s\2" % self.auth(source))
		elif len(arg) == 0:
			self.query("delete from vhosts where user = '%s'" % self.auth(source))
			self.msg(source, "Done.")
			for data in self.query("select host,username from online where uid = '%s'" % source):
				self.send(":%s CHGIDENT %s %s" % (self.bot, source, data[1]))
				self.send(":%s CHGHOST %s %s" % (self.bot, source, data[0]))
		else:
			self.msg(source, "Syntax: VHOST <vhost>")
