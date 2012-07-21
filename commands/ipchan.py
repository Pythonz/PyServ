from pyserv import Command

class ipchan(Command):
	help = "Forces an IP to join a channel"
	oper = 1

	def onCommand(self, uid, args):
		arg = args.split()
		
		if len(arg) == 0:
			self.msg(uid, "IP                 Channel")
			
			for data in self.query("select ip,channel from ipchan order by id"):
				self.msg(uid, "  {0} {1} {2}".format(data["ip"], " "*int(15-len(data["ip"])), data["channel"]))
				
			self.msg(uid, "End of list.")
		elif len(arg) == 1:
			self.msg(uid, "IP                 Channel")
			
			for data in self.query("select ip,channel from ipchan where channel = '%s' order by id" % arg[0]):
				self.msg(uid, "  {0} {1} {2}".format(data["ip"], " "*int(15-len(data["ip"])), data["channel"]))
				
			self.msg(uid, "End of list.")
		elif len(arg) == 2:
			if self.chanexist(arg[0]):
				entry = False
				
				for data in self.query("select * from ipchan where ip = '%s' and channel = '%s'" % (arg[1], arg[0])):
					entry = True
					
				if entry:
					self.msg(uid, "Delete %s from %s ..." % (arg[1], arg[0]))
					self.query("delete from ipchan where ip = '%s' and channel = '%s'" % (arg[1], arg[0]))
					self.msg(uid, "Done.")
				else:
					self.msg(uid, "Force %s to %s ..." % (arg[1], arg[0]))
					self.query("insert into ipchan (`ip`, `channel`) values ('%s', '%s')" % (arg[1], arg[0]))
					self.msg(uid, "Done.")
			else:
				self.msg(uid, "Invalid channel: "+arg[0])
		else:
			self.msg(uid, "Syntax: IPCHAN [<#channel> [<ip>]]")

	def onFantasy(self, uid, channel, args):
		self.onCommand(uid, channel + " " + args)
