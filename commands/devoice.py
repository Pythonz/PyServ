import pyserv

class devoice(pyserv.Command):
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
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
					self.mode(arg[0], "-{0} {1}".format("v"*len(arg[1:]), ' '.join(arg[1:])))
					if self.chanflag("p", arg[0]):
						for user in arg[1:]:
							uflag = self.getflag(self.uid(user), arg[0])
							if flag == "v":
								self.mode(arg[0], "+v "+user)
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: DEVOICE <#channel> [<nick> [<nick>]]")
