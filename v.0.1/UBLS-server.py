import socket, threading, json
import os, copy, sys, time

sys.setrecursionlimit(8192)
dirname = os.path.dirname(__file__) + "/"
serverSocket = socket.socket()
try:
	serverSocket.bind(("", 24678))
	print("[LOG]", "Successfully installed port for socket")
except Exception as exc:
	print("[ERROR]", "Failed to install port for socket")
	print("[EXCEPTION]", exc)
	input()
	exit()

worldFile = None
clients = []

with open(dirname+"server/settings.json", "r") as f:
	serverSettings = json.load(f)
autoSaveTime = serverSettings["autosaveTime"]

serverSocket.listen(1)
MAX_CLIENTS = 10
while True:
	a = input("[INPUT] (load <name> / newWorld) >>> ")
	if a[0:5].lower() == "load ":
		if not a[-5:] == ".json": a+=".json"
		if os.path.exists(dirname+"server/saves/"+a[5:]):
			with open(dirname+"server/saves/"+a[5:], "r") as f:
				serverBlocks = json.load(f)
			worldFile = dirname+"server/saves/"+a[5:]
			print("[LOG]", "Successfully loaded world "+a[5:])
			break
		else:
			print("[ERROR] {} does not exist".format(a[5:]))
	else:
		serverBlocks = []
		break
print("[INFO]", "Enter help to get help")

class Client:
	def __init__(self, socket, nickname, ID):
		self.socket = socket
		self.socket.settimeout(15)
		self.nickname = nickname
		self.id = ID
		self.mPos = [0, 0]
		self.level = 0
		self.updatedBlocks = []
		self.deletedBlocks = []
		self.newBlocks = []
		self.connecting = [False]
		self.thread = threading.Thread(target=self.thread)
		self.thread.start()
	def thread(self):
		global updatedBlocks1
		while running:
			# try:
			data = ""
			while True:
				_data = self.socket.recv(16384).decode("utf-8")
				if not _data: raise Exception()
				data += _data
				if data[-1] == "=":
					data = data[:-1]
					break
			data = json.loads(data)
			self.mPos = data["mPos"]
			self.level = data["myLevel"]
			self.connecting = data["connecting"]
			for i in data["newBlocks"]:
				ID = len(serverBlocks)
				serverBlocks.append(i)
				updatedBl = updateBlock(serverBlocks[ID])
				updatedBlocks1 = []
				if updatedBl != None: serverBlocks[ID] = updatedBl
				for c in clients:
					c.newBlocks.append(serverBlocks[ID])

			for i in data["deletedBlocks"]:
				for bl in serverBlocks:
					if i["pos"] == bl["pos"] and i["level"] == bl["level"]:
						for c in clients:
							c.deletedBlocks.append({"pos": bl["pos"], "level": bl["level"]})
						serverBlocks.remove(bl)
						updateBlock(bl)
						updatedBlocks1 = []
						break

			for i in data["updatedBlocks"]:
				for index, bl2 in enumerate(serverBlocks):
					if i["pos"] == bl2["pos"] and i["level"] == bl2["level"]:
						serverBlocks[index] = i
						updatedBl = updateBlock(serverBlocks[index])
						updatedBlocks1 = []
						if updatedBl != None: serverBlocks[index] = updatedBl
						break

			reply = {"newBlocks": [], "updatedBlocks": [], "deletedBlocks": []}
			reply["newBlocks"] = self.newBlocks
			self.newBlocks = []	
			reply["deletedBlocks"] = self.deletedBlocks
			self.deletedBlocks = []
			reply["updatedBlocks"] = self.updatedBlocks
			self.updatedBlocks = []



			reply["PlayersData"] = [{"mPos": c.mPos, "nickname": c.nickname, "level": c.level, "connecting": c.connecting} for c in clients if c.id != self.id]
			reply = json.dumps(reply) + "="
			self.socket.send(reply.encode())
			time.sleep(0.015)
			# except Exception as ex:
			# 	print("[EXCEPTION]", ex)
			# 	break
		print("[INFO] {} has disconnected".format(self.nickname))
		self.socket.close()
		clients.remove(self)

updatedBlocks1 = []
def updateBlock(block):
	global updatedBlocks1
	exists = False
	for bl2 in updatedBlocks1:
		if bl2["pos"] == block["pos"] and bl2["level"] == block["level"]:
			exists = True
			break
	updatedBlocks1.append(block)
	if not exists:
		if block["type"] == "Generator" or block["type"] == "Lever":
			for bl, inID in block["connections"]:
				found = False
				for index, bl2 in enumerate(serverBlocks):
					if bl2["pos"] == bl["pos"] and bl2["level"] == bl["level"]:
						found = True
						bl2["inputs"][inID] = block["out"]
						updatedBl = updateBlock(bl2)
						if updatedBl != None: serverBlocks[index] = updatedBl
						break
				if not found: block["connections"].remove([bl, inID])
		elif block["type"] == "Not" or block["type"] == "OR":
			for index, b in enumerate(block["is_connected"]):
				if b[0]:
					found = False
					for bl in serverBlocks:
						if bl["pos"] == b[1]["pos"] and bl["level"] == b[1]["level"]:
							found = True
							block["inputs"][b[2]] = bl["out"]
							break
					if not found: block["is_connected"][index], block["inputs"][index] = [False], False
				elif block["inputs"][index] == True:
					block["inputs"][index] = False

			if block["type"] == "Not": block["out"] = not block["inputs"][0]
			else: block["out"] = block["inputs"][0] or block["inputs"][1] or block["inputs"][2]
			for bl, inID in block["connections"]:
				found = False
				for index, bl2 in enumerate(serverBlocks):
					if bl2["pos"] == bl["pos"] and bl2["level"] == bl["level"]:
						found = True
						bl2["inputs"][inID] = block["out"]
						updatedBl = updateBlock(bl2)
						if updatedBl != None: serverBlocks[index] = updatedBl
						break
				if not found: block["connections"].remove([bl, inID])
		elif block["type"] == "Lamp":
			for index, b in enumerate(block["is_connected"]):
				if b[0]:
					found = False
					for bl in serverBlocks:
						if bl["pos"] == b[1]["pos"] and bl["level"] == b[1]["level"]:
							found = True
							block["inputs"][b[2]] = bl["out"]
							break
					if not found: block["is_connected"][index], block["inputs"][index] = [False], False
				elif block["inputs"][index] == True:
					block["inputs"][index] = False
		for c in clients:
			c.updatedBlocks.append(block)
		return block


def globalUpdateCycle():
	global clients, serverBlocks, worldFile
	while True:
		a = input()
		if a[0:10].lower() == "saveworld ":
			if not a[-5:] == ".json": a+=".json"
			if not os.path.exists(dirname+"server"): os.mkdir(dirname+"server")
			if not os.path.exists(dirname+"server/saves"): os.mkdir(dirname+"server/saves")
			if not os.path.exists(dirname+"server/saves/"+a[10:]):
				with open(dirname+"server/saves/"+a[10:], "w") as f:
					json.dump(serverBlocks, f)
				worldFile = dirname+"server/saves/"+a[10:]
				print("[LOG]", "Successfully saved world "+a[10:])
			else:
				b = input("[INPUT] {} is already exists. Do you want to overwrite it? (y/n)".format(a[10:]))
				if b == "y":
					with open(dirname+"server/saves/"+a[10:], "w+") as f:
						json.dump(serverBlocks, f)
					worldFile = dirname+"server/saves/"+a[10:]
					print("[LOG]", "Successfully overwrited world "+a[10:])
		elif a[0:4].lower() == "save":
			try:
				with open(worldFile, "w") as f:
					json.dump(serverBlocks, f)
			except: print("[ERROR]", "Use saveworld <name> command to save your world to a new file")
			else: print("[LOG]", "Successfully saved world")
		elif a[0:18].lower() == "set_autosave_time ":
			if a[18:].isdigit():
				serverSettings["autosaveTime"] = int(a[18:])
				autoSaveTime = int(a[18:])
				with open(dirname+"server/settings.json", "w") as f:
					json.dump(serverSettings, f)
		elif a[0:4].lower() == "help":
			print("[Help]", "saveworld <name> = save your current world to a new or an existing file")
			print("      ", "save = save your current world to the selected file by using saveworld command")
			print("      ", "set_autosave_time <number> = set the frequency of auto-saving the world to the selected file")
			print("      ", "help = this message")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			print("      ", "")
			
previousAutoSave = time.time()
def AutoSave():
	global previousAutoSave, worldFile, serverBlocks
	while running:
		if worldFile != None:
			if time.time() - previousAutoSave >= autoSaveTime:
				with open(worldFile, "w") as f:
					json.dump(serverBlocks, f)
				print("[LOG]", "Autosaved world")
				previousAutoSave = time.time()
		time.sleep(2)

running = True
globalUpdateCycleThread = threading.Thread(target=globalUpdateCycle)
globalUpdateCycleThread.start()
AutoSaveThread = threading.Thread(target=AutoSave)
AutoSaveThread.start()
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