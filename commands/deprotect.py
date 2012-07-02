from pyserv import Command
from fnmatch import fnmatch

class deprotect(Command):
	help = "Removes admin (+a) flag from you or someone on the channel"
	nauth = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) == 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a":
					self.mode(arg[0], "-ao {0} {0}".format(source))
					self.msg(source, "Done.")
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				
				if flag == "n" or flag == "q":
					for user in self.userlist(arg[0]):
						for target in arg[1:]:
							if fnmatch(self.nick(user).lower(), target.lower()):
								self.mode(arg[0], "-ao "+user+" "+user)
								
								if self.chanflag("p", arg[0]):
									uflag = self.getflag(user, arg[0])
									
									if uflag == "a":
										self.mode(arg[0], "+ao "+user+" "+user)
									if uflag == "o":
										self.mode(arg[0], "+o "+user)
										
					self.msg(source, "Done.")
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		else:
			self.msg(source, "Syntax: DEPROTECT <#channel> [<nick> [<nick>]]")

	def onFantasy(self, uid, chan, args):
		self.onCommand(uid, chan + " " + args)
