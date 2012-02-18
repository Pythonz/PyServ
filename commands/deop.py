import pyserv

class deop(pyserv.Command):
	help = "Removes op (+o) flag from you or someone on the channel"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o":
					self.mode(arg[0], "-o {0}".format(source))
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o":
					self.mode(arg[0], "-{0} {1}".format("o"*len(arg[1:]), ' '.join(arg[1:])))
					if self.chanflag("p", arg[0]):
						for user in arg[1:]:
							uflag = self.getflag(self.uid(user), arg[0])
							if uflag == "o":
								self.mode(arg[0], "+o "+user)
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: DEOP <#channel> [<nick> [<nick>]]")
