#!/usr/bin/env python

import subprocess

subprocess.Popen("python setup.py build", shell=True, cwd="deps/mysql").wait()
subprocess.Popen("python setup.py install", shell=True, cwd="deps/mysql").wait()

