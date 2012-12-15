from pyserv import Command
from fnmatch import fnmatch

class op(Command):
	help = "Sets op (+o) flag to you or someone on the channel"
	nauth = 1

	def onCommand(self, source, args):
		arg = args.split()
		
		if len(arg) == 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a" or flag == "o":
					self.mode(arg[0], "+o {0}".format(source))
					self.msg(source, "Done.")
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				
				if flag == "n" or flag == "q" or flag == "a" or flag == "o":
					for user in self.userlist(arg[0]):
						for target in arg[1:]:
							if fnmatch(self.nick(user).lower(), target.lower()):
								self.mode(arg[0], "+o "+user)
								
								if self.chanflag("b", arg[0]):
									uflag = self.getflag(user, arg[0])
									
									if uflag != "o" and uflag != "a" and uflag != "q" and uflag != "n":
										self.mode(arg[0], "-o "+user)
										
					self.msg(source, "Done.")
				else:
					self.msg(source, "Denied.")
			else:
				self.msg(source, "Invalid channel")
		else:
			self.msg(source, "Syntax: OP <#channel> [<nick> [<nick>]]")

	def onFantasy(self, uid, chan, args):
		flag = self.getflag(uid, chan)
		
		if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
			self.onCommand(uid, chan + " " + args)
