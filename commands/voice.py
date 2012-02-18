import pyserv

class voice(pyserv.Command):
	help = "Sets voice (+v) flag to you or someone on the channel"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h" or flag == "v":
					self.mode(arg[0], "+v {0}".format(source))
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		elif len(arg) > 2:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
					self.mode(arg[0], "+{0} {1}".format("v"*len(arg[1:]), ' '.join(arg[1:])))
					if self.chanflag("b", arg[0]) and not self.chanflag("v", arg[0]):
						for user in arg[1:]:
							uflag = self.getflag(self.uid(user), arg[0])
							if uflag != "v" and uflag != "h" uflag != "o" and uflag != "a" and uflag != "q" and uflag != "n":
								self.mode(arg[0], "-v "+user)
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: DEVOICE <#channel> [<nick> [<nick>]]")
