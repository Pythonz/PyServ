#!/usr/bin/env python

from subprocess import Popen

Popen("python setup.py build", cwd="deps/mysql").wait()
Popen("python setup.py install", cwd="deps/mysql").wait()
