from pyserv import Command

class spamscan(Command):
	help = "Sets the spam settings of your channel (chanflag s)"
	nauth = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 1:
			if self.chanexist(arg[0]):
				flag = self.getflag(uid, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
					for data in self.query("select spamscan from channelinfo where name = '%s'" % arg[0]):
						self.msg(uid, "Spamscan settings: "+data["spamscan"])
				else:
					self.msg(uid, "Denied.")
			else:
				self.msg(uid, "Invalid channel: "+arg[0])
		elif len(arg) == 2:
			if self.chanexist(arg[0]):
				flag = self.getflag(uid, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a":
					if arg[1].find(":") != -1:
						if arg[1].split(":")[0].isdigit() and arg[1].split(":")[1].isdigit():
							self.query("update channelinfo set spamscan = '%s' where name = '%s'" % (arg[1], arg[0]))
							self.msg(uid, "Done.")
						else:
							self.msg(uid, "Invalid spamscan settings '%s'. Example: '10:5'." % arg[1])
					else:
						self.msg(uid, "Invalid spamscan settings '%s'. Example: '10:5'." % arg[1])
				else:
					self.msg(uid, "Denied.")
			else:
				self.msg(uid, "Invalid channel: "+arg[0])
		else:
			self.msg(uid, "Syntax: SPAMSCAN <#channel> [<messages:seconds>]")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan + " " + args)
