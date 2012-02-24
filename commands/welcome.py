from pyserv import Command

class welcome(Command):
	nauth = 1
	help = "Sets a welcome message for your channel"
	def onCommand(self, source, args):
		import _mysql
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				entry = False
				for data in self.query("select name,welcome from channelinfo where name = '{0}'".format(arg[0])):
					self.msg(source, "[{0}] {1}".format(data["name"], data["welcome"]))
					entry = True
				if not entry:
					self.msg(source, "Channel {0} does not exist".format(arg[0]))
			else: self.msg(source, "Invalid channel")
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				welcome = _mysql.escape_string(' '.join(arg[1:]))
				if flag == "n" or flag == "q" or flag == "a":
					self.query("update channelinfo set welcome = '{0}' where name = '{1}'".format(welcome, arg[0]))
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: WELCOME <#channel> [<text>]")
