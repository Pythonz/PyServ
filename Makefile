CC = python
CFLAGS =

all: deps/
	@cd deps/mysql
	@$(CC) setup.py install
	@echo " ----------------------------"
	@echo "|          finished          |"
	@echo " ----------------------------"

install: deps/
	@cd deps/mysql
	@$(CC) setup.py install
	@echo " ----------------------------"
	@echo "|          finished          |"
	@echo " ----------------------------"
