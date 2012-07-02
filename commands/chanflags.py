from pyserv import Command

class chanflags(Command):
	help = "Sets flags for your channel"
	nauth = 1

	def onCommand(self, source, args):
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
		mode.append("b")
		desc.append("Bitchmode")
		mode.append("s")
		desc.append("Spamscan, prevents channel flooding")
		mode.append("f")
		desc.append("Fantasy commands")
		mode.append("k")
		desc.append("Sign kicks with Q")
		mode.append("c")
		desc.append("Display count at Q-kicks")
		arg = args.split()
		
		if len(arg) == 1:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "q" or self.getflag(source, arg[0]) == "a":
					for channel in self.query("select name,flags from channelinfo where name = '{0}'".format(arg[0])):
						self.msg(source, "Current flags for {0}: {1}".format(channel["name"], channel["flags"]))
				else:
					self.msg(source, "No permission")
			elif arg[0] == "?":
				listed = 0
				
				while listed != len(mode):
					self.msg(source, "{0} = {1}".format(mode[listed], desc[listed]))
					listed += 1
			else:
				self.msg(source, "Invalid channel '{0}'".format(arg[0]))
		elif len(arg) == 2:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) == "n" or self.getflag(source, arg[0]) == "a":
					for channel in self.query("select name from channelinfo where name = '{0}'".format(arg[0])):
						flags = ''.join([char for char in arg[1] if char in ''.join(mode)])
						self.query("update channelinfo set flags = '{0}' where name = '{1}'".format(flags, channel["name"]))
						self.msg(source, "New flags for {0}: {1}".format(channel["name"], flags))
				else:
					self.msg(source, "No permission")
			else:
				self.msg(source, "Invalid channel '{0}'".format(arg[0]))
		else:
			self.msg(source, "Syntax: CHANFLAGS <#channel> [<flags>]")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan + " " + args)
