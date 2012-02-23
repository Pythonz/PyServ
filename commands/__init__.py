import os

for cmd in os.listdir("commands"):
	if cmd.endswith(".py"):
		cmd = ' '.join(cmd.split(".")[:-1])
		if cmd != "__init__":
			if not sys.modules.has_key("commands."+cmd):
				exec("import commands."+cmd)
			else:
				exec("reload(commands."+cmd+")")

for module in dir(commands):
	if sys.modules.has_key("commands."+module):
		if not os.access("commands/"+module+".py", os.F_OK):
			exec("del commands."+module)
			exec("""del sys.modules["commands.%s"]""" % module)
