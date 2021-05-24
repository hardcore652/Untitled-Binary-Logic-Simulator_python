def updateBlock(block):
	if block["type"] == "Cable":
		block["connections"] = []
		block["signalPower"] = 0
		chain = []
		_list = []
		pos1 = [ [block["pos"][0]-1, block["pos"][1]], [block["pos"][0]+1, block["pos"][1]], [block["pos"][0], block["pos"][1]-1], [block["pos"][0], block["pos"][1]+1] ]
		for bl2 in serverBlocks:
			if bl2["type"] == "Cabel" and bl2["level"] == block["level"] and bl2["pos"] in pos1:
				chain.append(bl2)
				_list.append(bl2)
		while _list != []
			_block = _list.pop()
			pos2 = [ [_block["pos"][0]-1, _block["pos"][1]], [_block["pos"][0]+1, _block["pos"][1]], [_block["pos"][0], _block["pos"][1]-1], [_block["pos"][0], _block["pos"][1]+1] ]
			if _block["type"] == "Cabel" and _block["level"] == chain[-1]["level"] and _block["pos"] in pos2:

		for bl2 in serverBlocks:
			if (bl2["type"] == "Cable" or bl2["type"] == "Generator") and bl2["level"] == block["level"]:
				if list(bl2["pos"]) == pos1: block["connections"].append(1)
				if list(bl2["pos"]) == pos2: block["connections"].append(2)
				if list(bl2["pos"]) == pos3: block["connections"].append(3)
				if list(bl2["pos"]) == pos4: block["connections"].append(4)
				if bl2["type"] == "Cable" and list(bl2["pos"]) in [pos1, pos2, pos3, pos4] and block["signalPower"]+1 < bl2["signalPower"]: block["signalPower"] = bl2["signalPower"] - 1
				elif bl2["type"] == "Generator" and list(bl2["pos"]) in [pos1, pos2, pos3, pos4]: block["signalPower"] = 15


	return block