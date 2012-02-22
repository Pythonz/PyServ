import pyserv

class chanlev(pyserv.Command):
	help = "Edits your channel records"
	nauth = 1
	def onCommand(self, source, args):
		arg = args.split()
		if len(arg) == 1:
			if arg[0].startswith("#"):
				if self.getflag(source, arg[0]) != "0":
					channel = arg[0]
					self.msg(source, "Known users on {0}:".format(channel))
					self.msg(source, "Username               Flag")
					for data in self.query("select user,flag from channels where channel='{0}'".format(channel)):
						self.msg(source, " {0} {1} {2}".format(data[0], " "*int(24-len(data[0])), data[1]))
					self.msg(source, "End of list.")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		elif len(arg) == 2:
			channel = arg[0]
			if channel.startswith("#"):
				if arg[1].startswith("#"):
					username = arg[1][1:]
					entry = False
					user = False
					for data in self.query("select name from users where name = '%s'" % username):
						user = True
					for data in self.query("select channel,flag from channels where user = '%s' and channel = '%s'" % (username, channel)):
						self.msg(source, "Flags for #"+username+" on "+data[0]+": +"+data[1])
						channel = data[0]
						entry = True
					if user and not entry: self.msg(source, "User #"+username+" is not known on "+channel+".")
					elif not user: self.msg(source, "Can't find user #"+username+".")
				else:
					username = self.auth(self.uid(arg[1]))
					entry = False
					for data in self.query("select channel,flag from channels where user = '%s' and channel = '%s'" % (username, channel)):
						self.msg(source, "Flags for "+arg[1]+" on "+data[0]+": +"+data[1])
						channel = data[0]
						entry = True
					if username != 0 and not entry: self.msg(source, "User "+arg[1]+" is not known on "+channel+".")
					if username == 0: self.msg(source, "Can't find user "+arg[1]+".")
			else: self.msg(source, "Invalid channel")
		elif len(arg) == 3:
			channel = arg[0]
			if channel.startswith("#"):
				entry = False
				for channels in self.query("select channel from channels where user = '%s' and flag = 'n'" % self.auth(source)):
					if channel.lower() == str(channels[0]).lower():
						entry = True
						channel = str(channels[0])
				if entry:
					if arg[1].startswith("#"):
						username = arg[1][1:]
						entry = False
						for data in self.query("select name from users where name = '%s'" % username):
							if str(self.auth(source)).lower() != username.lower():
								self.query("delete from channels where channel = '%s' and user = '%s'" % (channel, username))
								if arg[2][0] != "-":
									self.query("insert into channels values ('%s','%s','%s')" % (channel, username, arg[2][0]))
									for data in self.sid(username):
										self.flag(data)
										uflag = self.getflag(data, arg[0])
										if uflag != "v" and not self.chanflag("v", arg[0]):
											self.mode(arg[0], "-v "+data)
										if uflag != "h":
											self.mode(arg[0], "-h "+data)
										if uflag != "o":
											self.mode(arg[0], "-o "+data)
										if uflag != "a":
											self.mode(arg[0], "-a "+data)
										if uflag != "q":
											self.mode(arg[0], "-q "+data)
								else:
									flag = self.getflag(username, arg[0])
									self.query("delete from channels where channel = '%s' and user = '%s'" % (arg[0], username))
									if not self.chanflag("v", arg[0]) and flag == "v":
										for user in self.sid(username):
											self.mode(arg[0], "-v "+user)
									else:
										for user in self.sid(username):
											self.mode(arg[0], "-"+flag+" "+user)
								self.msg(source, "Done.")
							else: self.msg(source, "You cannot change your own flags!")
							entry = True
						if not entry: self.msg(source, "Can't find user "+arg[1]+".")
					else:
						username = self.auth(self.uid(arg[1]))
						if username != 0:
							for data in self.query("select name from users where name = '%s'" % username):
								if str(self.auth(source)).lower() != username.lower():
									self.query("delete from channels where channel = '%s' and user = '%s'" % (channel, username))
									if arg[2][0] != "-":
										self.query("insert into channels values ('%s','%s','%s')" % (channel, username, arg[2][0]))
										for data in self.sid(username):
											self.flag(data)
											uflag = self.getflag(data, arg[0])
											if uflag != "v" and not self.chanflag("v", arg[0]):
												self.mode(arg[0], "-v "+data)
											if uflag != "h":
												self.mode(arg[0], "-h "+data)
											if uflag != "o":
												self.mode(arg[0], "-o "+data)
											if uflag != "a":
												self.mode(arg[0], "-a "+data)
											if uflag != "q":
												self.mode(arg[0], "-q "+data)
									else:
										flag = self.getflag(username, arg[0])
										self.query("delete from channels where channel = '%s' and user = '%s'" % (arg[0], username))
										if not self.chanflag("v", arg[0]) and flag == "v":
											for user in self.sid(username):
												self.mode(arg[0], "-v "+user)
										else:
											for user in self.sid(username):
												self.mode(arg[0], "-"+flag+" "+user)
									self.msg(source, "Done.")
								else: self.msg(source, "You cannot change your own flags!")
								entry = True
							if not entry: self.msg(source, "Can't find user "+arg[1]+".")
				else: self.msg(source, "Denied.")
			else: self.msg(source, "Invalid channel")
		else: self.msg(source, "Syntax: CHANLEV <#channel> [<user> [<flag>]]")
