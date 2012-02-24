from pyserv import Command

class version(Command):
	help = "Shows version of services"
	def onCommand(self, source, args):
		from hashlib import md5
		file = open("version", "r")
		version = file.read()
		file.close()
		options = list()
		if self.ssl:
			options.append("SSL")
		if self.ipv6:
			options.append("IPv6")
		if self.status:
			options.append("Status")
		self.msg(source, "PyServ {0}".format(version))
		self.msg(source, "Hash: {0}".format(md5(open("pyserv.py","r").read()).hexdigest()))
		if len(options) != 0:
			self.msg(source, "Options: {0}".format(', '.join(options)))
		self.msg(source, "Developed by Pythonz (https://github.com/Pythonz). Suggestions to pythonz@skyice.tk.")
