from pyserv import Command

class ipchan(Command):
	help = "Forces an IP to join a channel"
	oper = 1
	def onCommand(self, uid, args):
		arg = args.split()
		if len(arg) == 0:
			self.msg(uid, "IP forced channels:")
			self.msg(uid, "  IP                 Channel")
			for data in self.query("select ip,channel from ipchan"):
				self.msg(uid, "  {0} {1} {2}".format(data["ip"], " "*int(15-len(data["ip"])), data["channel"]))
			self.msg(uid, "End of list.")
		if len(arg) == 1:
			self.msg(uid, "IP forced channels:")
			self.msg(uid, "  IP                 Channel")
			for data in self.query("select ip,channel from ipchan where ip = '%s'" % arg[0]):
				self.msg(uid, "  {0} {1} {2}".format(data["ip"], " "*int(15-len(data["ip"])), data["channel"]))
			self.msg(uid, "End of list.")
		if len(arg) == 2:
			if self.chanexist(arg[1]):
				entry = False
				for data in self.query("select * from ipchan where ip = '%s' and channel = '%s'" % (arg[0], arg[1])):
					entry = True
				if entry:
					self.msg(uid, "Delete %s from %s ..." % (arg[0], arg[1]))
					self.query("delete from ipchan where ip = '%s' and channel = '%s'" % (arg[0], arg[1]))
					self.msg(uid, "Done.")
				else:
					self.msg(uid, "Force %s to %s ..." % (arg[0], arg[1]))
					self.query("insert into ipchan values ('%s', '%s')" % (arg[0], arg[1]))
					self.msg(uid, "Done.")
			else:
				self.msg(uid, "Invalid channel: "+arg[1])
		else:
			self.msg(uid, "Syntax: IPCHAN [<ip> [<channel>]]")
