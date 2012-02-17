import pyserv

class chanflags(pyserv.Command):
	help = "Sets flags for your channel"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "q" or self.getflag(source, arg[0]) == "a":
					for channel in self.query("select name,flags from channelinfo where name = '{0}'".format(arg[0])):
						self.msg(source, "Current flags for {0}: {1}".format(channel[0], channel[1]))
				else:
					self.msg(source, "No permission")
			elif arg[0] == "?":
				mode = list()
				desc = list()
				mode.append("p")
				desc.append("Channel rights Protection")
				mode.append("v")
				desc.append("Autovoice in channel")
				mode.append("t")
				desc.append("Topic save")
				mode.append("m")
				desc.append("Modes enforcement")
				mode.append("w")
				desc.append("Welcome message on join")
				mode.append("l")
				desc.append("Used for channel logs")
				mode.append("e")
				desc.append("Enforce bans")
				listed = 0
				while listed != len(mode):
					self.msg(source, "{0}: {1}".format(mode[listed], desc[listed]))
					listed += 1
			else:
				self.msg(source, "Invalid channel '{0}'".format(arg[0]))
		elif len(arg) == 2:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "a":
					for channel in self.query("select name from channelinfo where name = '{0}'".format(arg[0])):
						self.query("update channelinfo set flags = '{0}' where name = '{1}'".format(arg[1], channel[0]))
						self.msg(source, "New flags for {0}: {1}".format(channel[0], arg[1]))
				else:
					self.msg(source, "No permission")
			else:
				self.msg(source, "Invalid channel '{0}'".format(arg[0]))
		else:
			self.msg(source, "Syntax: CHANFLAGS <#channel> [<flags>]")
