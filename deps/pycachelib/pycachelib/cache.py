from socket import socket, AF_INET, AF_INET6, SOCK_STREAM

class Cache:
	def __init__(self, inet=AF_INET, stream=SOCK_STREAM):
		self.socket = socket(inet, stream)
		return None

	def connect(self, ip="127.0.0.1", port=1270):
		self.socket.connect((ip, port))

	def stor(self, string, data):
		self.socket.send("STOR " + string + " " + data + "\n")
		recv = self.socket.recv(10).rstrip()
		if recv == "OK":
			return True
		return False

	def retr(self, string, maxlen=1024):
		self.socket.send("RETR " + string + "\n")
		recv = self.socket.recv(int(maxlen)).rstrip()
		if recv != "ERROR":
			return ' '.join(recv.split()[2:])
		return False

	def drop(self, string):
		self.socket.send("DROP " + string + "\n")
		recv = self.socket.recv(10).rstrip()
		if recv == "OK":
			return True
		return False

	def rena(self, string, newstring):
		self.socket.send("RENA " + string + " " + newstring + "\n")
		recv = self.socket.recv(10).rstrip()
		if recv == "OK":
			return True
		return False

	def exis(self, string):
		self.socket.send("EXIS " + string + "\n")
		recv = self.socket.recv(10).rstrip()
		if recv == "OK":
			return True
		return False

	def line(self, integer):
		self.socket.send("LINE " + integer + "\n")
		recv = self.socket.recv(10).rstrip()
		if recv == "OK":
			return True
		return False

	def dele(self):
		self.socket.send("DELE\n")
		recv = self.socket.recv(10).rstrip()
		if recv == "OK":
			return True
		return False

	def conn(self):
		self.socket.send("CONN\n")
		recv = self.socket.recv(10).rstrip()
		if recv = "OK":
			return True
		return False

	def quit(self):
		self.socket.send("QUIT\n")
		recv = self.socket.recv(10).rstrip()
		if recv == "OK":
			self.socket.close()
			return True
		return False

	def close(self):
		self.socket.close()

	def reconnect(self, ip="127.0.0.1", port=1270):
		self.socket.close()
		self.socket.connect((ip, port))