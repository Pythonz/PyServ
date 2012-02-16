import os

for cmd in os.listdir("commands"):
	if cmd.endswith(".py"):
		cmd = ' '.join(cmd.split(".")[:-1])
		if cmd != "__init__":
			exec("import commands."+cmd)
