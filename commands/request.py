from pyserv import Command

class request(Command):
	help = "Requests Q for your channel"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				exists = False
				for data in self.query("select channel from channels where channel = '%s'" % arg[0]):
						exists = True
				if not exists:
					if not self.suspended(arg[0]):
						self.query("insert into channelinfo values ('%s', '', '', '', '', '10:5')" % arg[0])
						self.query("insert into channels values ('%s','%s','n')" % (arg[0], self.auth(source)))
						self.join(arg[0])
						self.mode(arg[0], "+q {0}".format(source))
						self.msg(source, "Channel %s has been registered for you" % arg[0])
					else:
						self.msg(source, "Channel " + arg[0] + " is suspended: " + self.suspended(arg[0]))
				else:
					self.msg(source, "Channel %s is already registered" % arg[0])
			else: self.msg(source, "Invalid channel")
		else:
			self.msg(source, "Syntax: REQUEST <#channel>")
