from pyserv import Command

class chanmode(Command):
	help = "Sets modes for your channel"
	nauth = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) == 1:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "q" or self.getflag(source, arg[0]) == "a":
					for channel in self.query("select name,modes from channelinfo where name = '{0}'".format(arg[0])):
						self.msg(source, "Current modes for {0}: {1}".format(channel["name"], channel["modes"]))
				else:
					self.msg(source, "No permission")
			else:
				self.msg(source, "Invalid channel '{0}'".format(arg[0]))
		elif len(arg) == 2:
			modes = arg[1]
			
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "q" or self.getflag(source, arg[0]) == "a":
					for channel in self.query("select name from channelinfo where name = '{0}'".format(arg[0])):
						self.query("update channelinfo set modes = '{0}' where name = '{1}'".format(modes, channel["name"]))
						self.mode(channel["name"], modes)
						self.msg(source, "New modes for {0}: {1}".format(channel["name"], modes))
				else:
					self.msg(source, "No permission")
			else:
				self.msg(source, "Invalid channel '{0}'".format(arg[0]))
		else:
			self.msg(source, "Syntax: CHANMODE <#channel> [<modes>]")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan + " " + args)
