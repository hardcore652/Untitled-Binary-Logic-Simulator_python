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
dirname = os.path.dirname(__file__) + "/"
serverSocket.listen(1)
MAX_CLIENTS = 10
while True:
	a = input("[INPUT] (load <name> / newWorld) >>> ")
	if a[0:5].lower() == "load ":
		if not a[-5:] == ".json": a+=".json"
		if os.path.exists(dirname+"server/saves/"+a[5:]):
			with open(dirname+"server/saves/"+a[5:], "r") as f:
				serverBlocks = json.load(f)
				print("[LOG]", "Successfully loaded world "+a[5:])
				break
		else:
			print("[ERROR] {} does not exist".format(a[5:]))
	else:
		serverBlocks = []
		break


class Client:
	def __init__(self, socket, nickname, ID):
		self.socket = socket
		self.socket.settimeout(15)
		self.nickname = nickname
		self.id = ID
		self.mPos = [0, 0]
		self.level = 0
		self.updatedBlocks = []
		self.oldBlocks = copy.deepcopy(serverBlocks)
		self.thread = threading.Thread(target=self.thread)
		self.thread.start()
	def thread(self):
		while running:
			try:
				data = self.socket.recv(8192).decode("utf-8")
				if not data: break
				data = json.loads(data)
				self.mPos = data["mPos"]
				self.level = data["myLevel"]
				for i in data["newBlocks"]:
					ID = len(serverBlocks)
					serverBlocks.append(i)
					serverBlocks[ID] = updateBlock(serverBlocks[ID])

				for i in data["deletedBlocks"]:
					for bl in serverBlocks:
						if i["pos"] == bl["pos"] and i["level"] == bl["level"]:
							serverBlocks.remove(bl)

				for i in data["updatedBlocks"]:
					for index, bl2 in enumerate(serverBlocks):
						if i["pos"] == bl2["pos"] and i["level"] == bl2["level"]:
							serverBlocks[index] = i
							serverBlocks[index] = updateBlock(serverBlocks[index])

				reply = {"newBlocks": [], "updatedBlocks": [], "deletedBlocks": []}
				if len(self.oldBlocks) != len(serverBlocks):
					for bl in serverBlocks:
						exists = False
						for bl2 in self.oldBlocks:
							if bl["pos"] == bl2["pos"] and bl["level"] == bl2["level"]:
								exists = True
						if not exists:
							reply["newBlocks"].append(bl)
							self.oldBlocks.append(bl)
					for bl in self.oldBlocks:
						exists = False
						for bl2 in serverBlocks:
							if bl["pos"] == bl2["pos"] and bl["level"] == bl2["level"]:
								exists = True
						if not exists:
							reply["deletedBlocks"].append(bl)
							self.oldBlocks.remove(bl)
				reply["updatedBlocks"] = self.updatedBlocks
				self.updatedBlocks = []



				reply["PlayersData"] = [{"mPos": c.mPos, "nickname": c.nickname, "level": c.level} for c in clients if c.id != self.id]
				reply = json.dumps(reply) + "="
				self.socket.send(reply.encode())
			except Exception as ex:
				print("[EXCEPTION]", ex)
				break
		print("[INFO] {} has disconnected".format(self.nickname))
		self.socket.close()
		clients.remove(self)


def updateBlock(block):
	if block["type"] == "Generator" or block["type"] == "Lever":
		for bl, inID in block["connections"]:
			for index, bl2 in enumerate(serverBlocks):
				if bl2["pos"] == bl["pos"] and bl2["level"] == bl["level"]:
					bl2["inputs"][inID] = True
					serverBlocks[index] = updateBlock(bl2)
	elif block["type"] == "Not":
		for index, b in enumerate(block["is_connected"]):
			if b[0]:
				for bl in serverBlocks:
					if bl["pos"] == b[1]["pos"] and bl["level"] == b[1]["level"]:
						block["inputs"][b[2]] = bl["out"]
			elif block["inputs"][index] == True:
				block["inputs"][index] = False

		block["out"] = not block["inputs"][0]
		for bl, inID in block["connections"]:
			for index, bl2 in enumerate(serverBlocks):
				if bl2["pos"] == bl["pos"] and bl2["level"] == bl["level"]:
					bl2["inputs"][inID] = block["out"]
					serverBlocks[index] = updateBlock(bl2)
	elif block["type"] == "OR":
		for index, b in enumerate(block["is_connected"]):
			if b[0]:
				for bl in serverBlocks:
					if bl["pos"] == b[1]["pos"] and bl["level"] == b[1]["level"]:
						block["inputs"][b[2]] = bl["out"]
			elif block["inputs"][index] == True:
				block["inputs"][index] = False
		block["out"] = block["inputs"][0] or block["inputs"][1] or block["inputs"][2]
		for bl, inID in block["connections"]:
			for index, bl2 in enumerate(serverBlocks):
				if bl2["pos"] == bl["pos"] and bl2["level"] == bl["level"]:
					bl2["inputs"][inID] = block["out"]
					serverBlocks[index] = updateBlock(bl2)
	for c in clients:
		c.updatedBlocks.append(block)
	return block


def globalUpdateCycle():
	global clients
	while True:
		a = input()
		if a[0:10].lower() == "saveworld ":
			if not a[-5:] == ".json": a+=".json"
			if not os.path.exists(dirname+"server"): os.mkdir(dirname+"server")
			if not os.path.exists(dirname+"server/saves"): os.mkdir(dirname+"server/saves")
			if not os.path.exists(dirname+"server/saves/"+a[10:]):
				with open(dirname+"server/saves/"+a[10:], "w") as f:
					json.dump(serverBlocks, f)
					print("[LOG]", "Successfully saved world "+a[10:])
			else:
				b = input("[INPUT] {} is already exists. Do you want to overwrite it? (y/n)".format(a[10:]))
				if b == "y":
					with open(dirname+"server/saves/"+a[10:], "w+") as f:
						json.dump(serverBlocks, f)
						print("[LOG]", "Successfully overwrited world "+a[10:])

running = True
globalUpdateCycleThread = threading.Thread(target=globalUpdateCycle)
globalUpdateCycleThread.start()
while running:
	if len(clients) < MAX_CLIENTS:
		connection, address = serverSocket.accept()

		try:
			nickname = connection.recv(8192).decode("utf-8")
			data = {"newBlocks": serverBlocks}
			data = json.dumps(data) + "="
			connection.send(data.encode())
		except Exception as exc:
			print("[ERROR]", "An unexpected error occured while client was connecting")
			print("[EXCEPTION]", exc)
			continue

		print("[INFO]", "{} has connected".format(nickname))
		clients.append(Client(connection, nickname, len(clients)))