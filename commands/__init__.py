import os
import sys

for cmd in os.listdir("commands"):
	if cmd.endswith(".py"):
		cmd = ' '.join(cmd.split(".")[:-1])
		if cmd != "__init__":
			if "commands."+cmd not in sys.modules:
				exec("import commands."+cmd)
			else:
				exec("reload(commands."+cmd+")")
