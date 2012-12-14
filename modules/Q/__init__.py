import os
import sys

module = "Q"

for cmd in os.listdir("modules/" + module):
	if cmd.endswith(".py"):
		cmd = ' '.join(cmd.split(".")[:-1])
		
		if cmd != "__init__":
			if not sys.modules.has_key("modules." + module + "." + cmd):
				exec("import modules." + module + "." + cmd)
			else:
				exec("reload(modules." + module + "." + cmd + ")")
