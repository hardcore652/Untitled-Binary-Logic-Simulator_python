import socket, threading, json
import os, copy

serverSocket = socket.socket()
try:
	serverSocket.bind(("", 24678))
	print("[LOG]", "Successfully installed port for socket")
except Exception as exc:
	print("[ERROR]", "Failed to install port for socket")
	print("[EXCEPTION]", exc)
	input()
	exit()

clients = []
dirname = os.path.dirname(__file__)
serverSocket.listen(1)
MAX_CLIENTS = 10
serverBlocks = []

class Client:
	def __init__(self, socket, nickname, ID):
		self.socket = socket
		self.socket.settimeout(15)
		self.nickname = nickname
		self.id = ID
		self.mPos = [0, 0]
		self.oldBlocks = []
		self.thread = threading.Thread(target=self.thread)
		self.thread.start()
	def thread(self):
		while running:
			try:
				data = self.socket.recv(8192).decode("utf-8")
				if not data: break
				data = json.loads(data)
				self.mPos = data["mPos"]
				for i in data["newBlocks"]:
					serverBlocks.append(i)
				for i in data["deletedBlocks"]:
					for bl in serverBlocks:
						if i["pos"] == bl["pos"]:
							serverBlocks.remove(bl)
				reply = {"newBlocks": [], "updatedBlocks": [], "deletedBlocks": []}
				if len(self.oldBlocks) != len(serverBlocks):
					for bl in serverBlocks:
						if not bl["pos"] in [bl2["pos"] for bl2 in self.oldBlocks]:
							reply["newBlocks"].append(bl)
							self.oldBlocks.append(bl)
					for bl in self.oldBlocks:
						if not bl["pos"] in [bl2["pos"] for bl2 in serverBlocks]:
							reply["deletedBlocks"].append(bl)
							self.oldBlocks.remove(bl)
				for bl in self.oldBlocks:
					for bl2 in serverBlocks:
						if bl["pos"] == bl2["pos"] and bl != bl2:
							reply["updatedBlocks"].append(bl2)
							bl = copy.deepcopy(bl2)



				reply["PlayersData"] = [{"mPos": c.mPos, "nickname": c.nickname} for c in clients if c.id != self.id]
				self.socket.send(json.dumps(reply).encode())
			except Exception as ex:
				print("[EXCEPTION]", ex)
				break
		print("[INFO] {} has disconnected".format(self.nickname))
		self.socket.close()
		clients.remove(self)



def globalUpdateCycle():
	global clients
	while True:
		break

running = True
globalUpdateCycleThread = threading.Thread(target=globalUpdateCycle)
globalUpdateCycleThread.start()
while running:
	if len(clients) < MAX_CLIENTS:
		connection, address = serverSocket.accept()

		try:
			nickname = connection.recv(8192).decode("utf-8")
		except Exception as exc:
			print("[ERROR]", "An unexpected error occured while client was connecting")
			print("[EXCEPTION]", exc)
			continue

		print("[INFO]", "{} has connected".format(nickname))
		clients.append(Client(connection, nickname, len(clients)))