from pyserv import Command
from fnmatch import fnmatch

class devoice(Command):
	help = "Removes voice (+v) flag from you or someone on the channel"
	nauth = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) == 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h" or flag == "v":
					self.mode(arg[0], "-v {0}".format(source))
					self.msg(source, "Done.")
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
					for user in self.userlist(arg[0]):
						for target in arg[1:]:
							if fnmatch(self.nick(user).lower(), target.lower()):
								self.mode(arg[0], "-v "+user)
								
								if self.chanflag("p", arg[0]):
									uflag = self.getflag(user, arg[0])
									
									if uflag == "v":
										self.mode(arg[0], "+v "+user)
										
					self.msg(source, "Done.")
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		else:
			self.msg(source, "Syntax: DEVOICE <#channel> [<nick> [<nick>]]")

	def onFantasy(self, uid, chan, args):
		flag = self.getflag(uid, chan)
		
		if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
			self.onCommand(uid, chan + " " + args)
