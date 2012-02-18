import pyserv

class dehalfop(pyserv.Command):
	help = "Removes halfop (+h) flag from you or someone on the channel"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o" or flag == "h":
					self.mode(arg[0], "-h {0}".format(source))
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		elif len(arg) > 1:
			if arg[0].startswith("#"):
				flag = self.getflag(source, arg[0])
				if flag == "n" or flag == "q" or flag == "a" or flag == "o":
					self.mode(arg[0], "-{0} {1}".format("h"*len(arg[1:]), ' '.join(arg[1:])))
					self.msg(source, "Done.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: DEHALFOP <#channel> [<nick> [<nick>]]")
