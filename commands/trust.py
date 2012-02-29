from pyserv import Command

class trust(Command):
	help = "Manage IP trusts for your network"
	oper = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 0:
			for trust in self.query("select * from trust"):
				self.msg(source, "IP: {0} {2} Limit: {1}".format(trust["address"], trust["limit"], ' '*int(23-len(trust["address"]))))
		elif len(arg) == 1:
			entry = False
			for trust in self.query("select * from trust where address = '{0}'".format(arg[0])):
				entry = True
				self.query("delete from trust where address = '{0}'".format(trust["address"]))
			if entry:
				self.msg(source, "Trust for {0} has been deleted.".format(arg[0]))
				conns = 0
				nicks = list()
				for online in self.query("select nick from online where address = '{0}'".format(arg[0])):
					nicks.append(online["nick"])
					conns += 1
				for nick in nicks:
					self.msg(self.uid(nick), "Your trust has been set to '3'.")
				if conns > 3 and arg[0] != "0.0.0.0":
					for nick in nicks:
						self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
					self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.bot, arg[0], limit))
				elif conns == 3 and arg[0] != "0.0.0.0":
					for nick in nicks:
						self.msg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
			else:
				self.msg(source, "Trust for {0} does not exist.".format(arg[0]))
		elif len(arg) == 2:
			entry = False
			for trust in self.query("select * from trust where address = '{0}'".format(arg[0])):
				entry = True
			if entry:
				limit = filter(lambda x: x.isdigit(), arg[1])
				if limit != "":
					self.query("update trust set `limit` = '{0}' where address = '{1}'".format(limit, arg[0]))
					self.msg(source, "Trust for {0} has been set to {1}.".format(arg[0], limit))
					conns = 0
					nicks = list()
					invalid = False
					for online in self.query("select nick from online where address = '{0}'".format(arg[0])):
						nicks.append(online["nick"])
						conns += 1
					for nick in nicks:
						self.msg(self.uid(nick), "Your trust has been set to '{0}'.".format(limit))
					if conns > int(limit) and arg[0] != "0.0.0.0":
						for nick in nicks:
							self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
						self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.bot, arg[0], limit))
					elif conns == int(limit) and arg[0] != "0.0.0.0":
						for nick in nicks:
							self.msg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
					for username in self.query("select username from online where address = '{0}'".format(arg[0])):
						if username["username"].startswith("~"):
							for nick in nicks:
								self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
							self.send(":{0} GLINE *@{1} 1800 :You ignored the trust rules. Run an identd before you connect again.".format(self.bot, arg[0]))
				else:
					self.msg(source, "Invalid limit")
			else:
				limit = filter(lambda x: x.isdigit(), arg[1])
				if limit != "":
					self.query("insert into  trust values ('{1}','{0}')".format(limit, arg[0]))
					self.msg(source, "Trust for {0} has been set to {1}.".format(arg[0], limit))
					conns = 0
					nicks = list()
					for online in self.query("select nick from online where address = '{0}'".format(arg[0])):
						nicks.append(online["nick"])
						conns += 1
					for nick in nicks:
						self.msg(self.uid(nick), "Your trust has been set to '{0}'.".format(limit))
					if conns > int(limit) and arg[0] != "0.0.0.0":
						for nick in nicks:
							self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
						self.send(":{0} GLINE *@{1} 1800 :Connection limit ({2}) reached".format(self.bot, arg[0], limit))
					elif conns == int(limit) and arg[0] != "0.0.0.0":
						for nick in nicks:
							self.msg(nick, "Your IP is scratching the connection limit. If you need more connections please request a trust and give us a reason on #help.")
					for username in self.query("select username from online where address = '{0}'".format(arg[0])):
						if username["username"].startswith("~"):
							for nick in nicks:
								self.send(":{0} KILL {1} :G-lined".format(self.bot, nick))
							self.send(":{0} GLINE *@{1} 1800 :You ignored the trust rules. Run an identd before you connect again.".format(self.bot, arg[0]))
				else:
					self.msg(source, "Invalid limit")
		else: self.msg(source, "TRUST [<address> [<limit>]]")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, args)
