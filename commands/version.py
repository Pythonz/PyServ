import pyserv

class version(pyserv.Command):
	help = "Shows version of services"
	def onCommand(self, source, args):
		file = open("version", "r")
		version = file.read()
		file.close()
		options = list()
		if self.ssl:
			options.append("SSL")
		if self.ipv6:
			options.append("IPv6")
		self.msg(source, "PyServ {0}".format(version))
		if len(options) != 0:
			self.msg(source, "Options: {0}".format(' '.join(options)))
		self.msg(source, "Developed by Pythonz (https://github.com/Pythonz). Suggestions to pythonz@skyice.tk.")
		
