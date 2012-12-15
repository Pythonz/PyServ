from pyserv import Command

class usermodes(Command):
	help = "Shows your usermodes or changes it"
	nauth = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 0:
			for data in self.query("select modes from users where name = '%s'" % self.auth(uid)):
				self.msg(uid, "Current modes: "+data["modes"])
		elif len(arg) == 1:
			self.query("update users set modes = '%s' where name = '%s'" % (''.join([char for char in arg[0] if char.isalpha() or char == "+" or char == "-"]), self.auth(uid)))
			self.usermodes(uid)
			self.msg(uid, "Done.")
		else:
			self.msg(uid, "Syntax: USERMODES [<modes>]")