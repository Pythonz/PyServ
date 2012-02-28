from pyserv import Command, config
from _mysql import escape_string

class accban(Command):
	help = "Bans an account from " + config.get("SERVICES", "description")
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 1:
			self.msg(uid, "Account                 Reason")
			for data in self.query("select * from users where suspended != '0'"):
				self.msg(uid, "  {0} {1} {2}".format(data["name"], int(13-len(data["name"])), data["suspended"]))
			self.msg(uid, "End of list.")
		elif len(arg) == 1:
			entry = False
			if arg[0][0] == "?":
				if self.user(arg[0][1:]):
					self.msg(uid, "Suspend status of account " + arg[0][1:] + ": " + str(self.banned(arg[0][1:])))
				else:
					self.msg(uid, "Can't find user " + arg[0][1:])
			if self.user(arg[0]):
				self.query("update users set suspended = '0' where name = '%s'" % arg[0])
				self.msg(uid, "Done.")
			if not exists:
				self.msg(uid, "Can't find user " + arg[0])
		elif len(arg) > 1:
			if self.user(arg[0]):
				self.query("update users set suspended = '%s'" % escape_string(' '.join(arg[1:])))
				self.msg(uid, "Done.")
			else:
				self.msg(uid, "Can't find user " + arg[0])
