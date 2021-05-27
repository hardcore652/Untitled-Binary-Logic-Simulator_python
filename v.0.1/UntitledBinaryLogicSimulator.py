import pygame, time
import socket, threading, json
import os, copy, sys, math
from gameSettings import *

pygame.init()

mainFont = pygame.font.Font(dirname+"resources/UI/mainFont.ttf", mainFontSize) # Load fonts
FONT2 = pygame.font.Font(dirname+"resources/UI/mainFont.ttf", FONT2Size)
FONT3 = pygame.font.Font(dirname+"resources/UI/mainFont.ttf", FONT3Size)

clock = pygame.time.Clock() # Clock for fps limit


class Message: # Message is the text that disappears after the specified time has elapsed
	def __init__(self, x, y, text, timer, text_color = (255, 255, 255), font=FONT2, is_alive = True, mode="topleft"):
		self.text_color = text_color
		self.font = font
		self.alive_timer = timer
		self.pos = (x, y)
		self.mode = mode
		self.text = self.font.render(text, FONTaa, self.text_color)
		self.rect = pygame.Rect(0, 0, *self.text.get_size())
		exec("self.rect.{} = self.pos".format(self.mode))
		self.timer = time.time()
		self.is_alive = is_alive
		self.was_alive = self.is_alive

	def changeText(self, newText):
		self.text = self.font.render(newText, FONTaa, self.text_color)
		self.rect = pygame.Rect(0, 0, *self.text.get_size())
		exec("self.rect.{} = self.pos".format(self.mode))

	def draw(self, screen):
		curr_time = time.time()
		if self.is_alive and not self.was_alive:
			self.timer = curr_time
		if curr_time - self.timer >= self.alive_timer:
			self.is_alive = False
		self.was_alive = self.is_alive
		if self.is_alive:
			screen.blit(self.text, self.rect)

class Camera:
	def __init__(self):
		self.rect = pygame.Rect(0, 0, *screenSize)
		self.dragPos = [0, 0]
		self.startRectPos = self.rect.topleft
	def move(self, click, mousePos, keys):
		if click[1]:
			self.rect.x = self.startRectPos[0] - (mousePos[0] - self.dragPos[0]) * CAMERA_MOVING_MODIFIER
			self.rect.y = self.startRectPos[1] - (mousePos[1] - self.dragPos[1]) * CAMERA_MOVING_MODIFIER
		else:
			if keys[pygame.K_w]: self.rect.y -= CAMERA_MOVING_SPEED
			if keys[pygame.K_s]: self.rect.y += CAMERA_MOVING_SPEED
			if keys[pygame.K_a]: self.rect.x -= CAMERA_MOVING_SPEED
			if keys[pygame.K_d]: self.rect.x += CAMERA_MOVING_SPEED

		if self.rect.x < -50000: self.rect.x = -50000
		elif self.rect.x > 50000: self.rect.x = 50000
		if self.rect.y < -50000: self.rect.y = -50000
		elif self.rect.y > 50000: self.rect.y = 50000
	def onEventClick(self, mousePos):
		self.dragPos = mousePos
		self.startRectPos = self.rect.topleft
	def renderRect(self, _rect):
		rect = copy.copy(_rect)
		rect.x -= self.rect.x; rect.y -= self.rect.y
		return rect
	def renderPos(self, pos):
		pos[0] -= self.rect.x; pos[1] -= self.rect.y
		return pos
	def checkVisible(self, rect): return True if rect.x <= screenSize[0] and rect.right >= 0 and rect.y <= screenSize[1] and rect.bottom >= 0 else False
	def checkVPos(self, pos): return True if pos[0] <= screenSize[0] and pos[0] >= 0 and pos[1] <= screenSize[1] and pos[1] >= 0 else False

class BackgroundPreview(pygame.sprite.Sprite):
	def __init__(self, textures, x, y, width = SIZES["BackgroundPreview"][0], height = SIZES["BackgroundPreview"][1], text="", font=mainFont, text_color=(255,255,255), mode="topleft", tag=0, outlineThickn = 5):
		pygame.sprite.Sprite.__init__(self)
		self.rect = pygame.Rect(0, 0, width, height)
		exec("self.rect.{} = [x, y]".format(mode))
		self.texture = textures
		self.tag = tag
		self.text = font.render(text, FONTaa, text_color)
		self.text_rect = self.text.get_rect(bottom = self.rect.bottom - 10, centerx = self.rect.centerx)
		self.textBG = pygame.Surface(self.text.get_size())
		self.textBG.fill((0, 0, 0))
		self.textBG.set_alpha(70)
		self.choosed = False
		self.thickn = outlineThickn
		self.current_texture = 0
	def swapTexture(self):
		if len(self.texture) > 1:
			self.current_texture += 1
			if self.current_texture >= len(self.texture): self.current_texture = 0
	def on_MOUSEBUTTONUP(self, mPos):
		if uiObject_state(self.rect, mPos, True) == 2: self.choosed = True
	def draw(self, screen):
		self.text_rect.centerx = self.rect.centerx
		self.text_rect.bottom = self.rect.bottom - 10
		screen.blit(self.texture[self.current_texture], self.rect)
		screen.blit(self.textBG, self.text_rect)
		screen.blit(self.text, self.text_rect)
		if self.choosed: pygame.draw.rect(screen, (255, 255, 255), self.rect, self.thickn)



class Button(pygame.sprite.Sprite):
	def __init__(self, x, y, width=50, height=50, text="", color=(80, 80, 100), font=mainFont, tag=0, text_color=(255, 255, 255), mode="topleft", hl_color=None, pr_color=None):
		pygame.sprite.Sprite.__init__(self)
		self.rect = pygame.Rect(0, 0, width, height)
		exec("self.rect.{} = [x, y]".format(mode))
		self.color = color
		self.text_color = text_color
		self.tag = tag
		self.state = 0
		self.triggered = 0
		self.image = pygame.Surface((width, height))
		self.image.fill(color)
		self.text = font.render(text, FONTaa, self.text_color)
		self.text_rect = self.text.get_rect(center=self.rect.center)
		
		if pr_color == None:
			self.pr_color = []
			if self.color[0] > 170 and self.color[1] > 170 and self.color[2] > 170:
				for i in range(3): self.pr_color.append(color[i]-50)
			else:
				for i in range(3): self.pr_color.append(color[i]+50)
			if self.pr_color[0] > 255: self.pr_color[0] = 255
			if self.pr_color[1] > 255: self.pr_color[1] = 255
			if self.pr_color[2] > 255: self.pr_color[2] = 255
		else: self.pr_color = pr_color
		if hl_color == None:
			self.hl_color = []
			if self.color[0] > 170 and self.color[1] > 170 and self.color[2] > 170:
				for i in range(3): self.hl_color.append(color[i]-25)
			else:
				for i in range(3): self.hl_color.append(color[i]+25)
			if self.hl_color[0] > 255: self.hl_color[0] = 255
			if self.hl_color[1] > 255: self.hl_color[1] = 255
			if self.hl_color[2] > 255: self.hl_color[2] = 255
		else: self.hl_color = hl_color

	def update(self, mPos, clicked):
		self.state = uiObject_state(self.rect, mPos, clicked)
		if self.state == 1: self.image.fill(self.hl_color)
		elif self.state == 2: self.image.fill(self.pr_color)
		elif self.state == 0: self.image.fill(self.color)

	def on_MOUSEBUTTONUP(self, mPos):
		if uiObject_state(self.rect, mPos, True) == 2: self.triggered = True

	def eventTrigger(self):
		_event = self.triggered
		self.triggered = False
		return _event

	def draw(self, screen):
		screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

def uiObject_state(rect, mPos, clicked):
	state = 0
	if mPos[0] < rect.right and mPos[0] > rect.left and mPos[1] < rect.bottom and mPos[1] > rect.top:
		if clicked: state = 2
		else: state = 1
	return state

defaultSize = os.get_terminal_size()
if sys.platform == "win32": os.system("mode 50, 20")

animation_step = 0

data = [
	"",
	"",
	"IP: ...",
	"Nickname: ...",
	"",
	""
]

def clear():
	print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
def draw_title():
	clear()
	for i in current_screen: print(i)
while True:

	if animation_step == len(current_screen):
		for i in data: print(i)
		break
	else:
		current_screen[animation_step] = title_screen[animation_step]
	draw_title()
	print("\n\n\n\n\n")

	clock.tick(8)
	animation_step += 1
draw_title()
for i in data: print(i)
ip = input("Enter ip ")
address = (ip, 24678)
data[2] = "IP: "+str(address[0])+":"+str(address[1])
draw_title()
for i in data: print(i)
nick = input("Enter username ")
data[3] = "Nickname: "+nick
draw_title()
for i in data: print(i)
time.sleep(1)
clear()
if sys.platform == "win32": os.system("mode {}, {}".format(str(defaultSize.columns), str(defaultSize.lines)))

screen = pygame.display.set_mode(screenRes)
screenSize = screen.get_size()











clientSocket = socket.socket()

del ip
CloseButton = Button(screenSize[0] // 2 - 15, screenSize[1] // 2 + 25, 100, 50, "Close", color=(160, 100, 100), font=FONT2, tag="close", mode="topright")
RetryButton = Button(screenSize[0] // 2 + 15, screenSize[1] // 2 + 25, 100, 50, "Retry", font=FONT2, tag="retry", mode="topleft")

running = True

mPos = [0, 0]
camera = Camera()
while running:
	try:
		screen.fill((20, 20, 20))
		text = FONT3.render("Connecting...", FONTaa, (180, 180, 180))
		rect = text.get_rect(center=[screenSize[0] // 2, screenSize[1] // 2])
		screen.blit(text, rect)
		pygame.display.flip()
		clientSocket.connect(address)
		clientSocket.settimeout(15)
		clientSocket.send(nick.encode())
		data = ""
		while True:
			newData = clientSocket.recv(16384).decode("utf-8")
			if not newData: raise Exception()
			data += newData
			if data[-1] == "=":
				data = json.loads(data[0:-1])
				break
		ServerBlocks = data["newBlocks"]

		break
	except:
		try:
			text = FONT3.render("Failed to connect to {}:{}".format(str(address[0]), str(address[1])), FONTaa, (180, 180, 180))
			screen.fill((20, 20, 20))
			rect = text.get_rect(center=[screenSize[0] // 2, screenSize[1] // 2 - 40])
			screen.blit(text, rect)
			pygame.display.flip()
			while running:
				click = pygame.mouse.get_pressed()
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						pygame.quit()
						running = False
					if event.type == pygame.MOUSEMOTION:
						mPos = event.pos

				CloseButton.update(mPos, click[0])
				RetryButton.update(mPos, click[0])
				if CloseButton.state == 2:
					pygame.quit()
					running = False
				if RetryButton.state == 2:
					raise Exception()
				CloseButton.draw(screen)
				RetryButton.draw(screen)
				pygame.display.update([CloseButton.rect, RetryButton.rect])
				clock.tick(60)
		except: pass
connected = True
def socketThread():
	global clientSocket, running, connected, mPos, PlayersData, newBlocks, deletedBlocks, ServerBlocks, current_level, updatedBlocks, connecting
		
	while running:
		#try:
		data = {"mPos": [mPos[0] + camera.rect.x, mPos[1] + camera.rect.y], "newBlocks":newBlocks,
			"deletedBlocks": deletedBlocks, "updatedBlocks": updatedBlocks,
			"myLevel": current_level, "connecting": connecting}
		newBlocks = []
		deletedBlocks = []
		updatedBlocks = []
		clientSocket.send((json.dumps(data)+"=").encode())
		recieved = ""
		while True:
			_recieved = clientSocket.recv(16384).decode("utf-8")
			if not _recieved: running, connected = False, False
			recieved += _recieved
			if recieved[-1] == "=":
				recieved = recieved[:-1]
				break
		recieved = json.loads(recieved)
		PlayersData = recieved["PlayersData"]
		for bl in recieved["updatedBlocks"]:
			for index, bl2 in enumerate(ServerBlocks):
				if bl["pos"] == bl2["pos"] and bl["level"] == bl2["level"]:
					ServerBlocks[index] = bl
		for bl in recieved["newBlocks"]:
			ServerBlocks.append(bl)
		for bl in recieved["deletedBlocks"]:
			for bl2 in ServerBlocks:
				if bl["pos"] == bl2["pos"] and bl["level"] == bl2["level"]:
					ServerBlocks.remove(bl2)
		#except:
			# CloseButton.rect.centerx = screenSize[0] // 2
			# CloseButton.text_rect.centerx = screenSize[0] // 2
			# connected = False
			# break
PlayersData = []
newBlocks = []
deletedBlocks = []
updatedBlocks = []
pygame.mouse.set_visible(False)

def loadTextureGroup(path, count, size=[layoutCellSize, layoutCellSize]):
	group = []
	for i in range(count):
		group.append( pygame.transform.scale(pygame.image.load(dirname+path+str(i)+".png").convert_alpha(), size) )
	return group


backgroundControl = {}
backgroundControl["active"] = False

backgroundControl["SurfRect"] = pygame.Rect(0, screenSize[1] - backgroundControlSettings["surfaceHeight"], screenSize[0], backgroundControlSettings["surfaceHeight"])

backgroundControl["CloseBGCButton"] = Button(screenSize[0], backgroundControl["SurfRect"].top, 35, 35, "X", text_color=(255, 255, 255), color=(160, 0, 0), font=mainFont, tag="BGSclose", mode="topright")
backgroundControl["OpenBGCButton"] = Button(screenSize[0] - 5, screenSize[1] - 5, 117, 45, "Backgrounds", text_color=(10, 10, 10), color=(200, 170, 20), font=mainFont, tag="BGS", mode="bottomright")

backgroundControl["openAnim"] = 0
backgroundControl["closeAnim"] = 0

backgroundControlSettings["BackgroundImage"] = pygame.transform.scale(pygame.image.load(dirname+"resources/Backgrounds/BGSControl.png").convert_alpha(), SIZES["BGSControlBackground"])

surf = pygame.Surface((screenSize[0], backgroundControlSettings["surfaceHeight"]))
for x in range(math.ceil(screenSize[0] / SIZES["BGSControlBackground"][0])):
	for y in range(math.ceil(backgroundControlSettings["surfaceHeight"] / SIZES["BGSControlBackground"][1])):
		surf.blit(backgroundControlSettings["BackgroundImage"], (x * SIZES["BGSControlBackground"][0], y * SIZES["BGSControlBackground"][1]))
backgroundControl["BackgroundImage"] = surf



PlayerIndicatorImage = pygame.transform.scale(pygame.image.load(dirname+"resources/UI/friendIndic.png").convert_alpha(), SIZES["PlayerIndicator"])

CobblestoneImage = pygame.transform.scale(pygame.image.load(dirname+"resources/backgrounds/cobblestone.png").convert_alpha(), SIZES["BackgroundTile"])

GeneratorImage = pygame.transform.scale(pygame.image.load(dirname+"resources/blocks/generator.png").convert_alpha(), [layoutCellSize, layoutCellSize])
LeverImage = loadTextureGroup("resources/blocks/lever", 2)
NotImage = pygame.transform.scale(pygame.image.load(dirname+"resources/blocks/not.png").convert_alpha(), [layoutCellSize, layoutCellSize])
PGImage = pygame.transform.scale(pygame.image.load(dirname+"resources/blocks/pulse_gen.png").convert_alpha(), [layoutCellSize, layoutCellSize])
ORImage = pygame.transform.scale(pygame.image.load(dirname+"resources/blocks/or.png").convert_alpha(), [layoutCellSize, layoutCellSize])
LampImage = loadTextureGroup("resources/blocks/lamp", 2)

BlockControl = {"active": False, "openButton": Button(screenSize[0] - 5, backgroundControl["OpenBGCButton"].rect.top - 5, 117, 45, "Blocks", text_color=(10, 10, 10), color=(20, 200, 20), font=mainFont, tag="Blocks", mode="bottomright")}

BACKGROUNDS = { }
BACKGROUNDS["cobblestone"] = pygame.Surface((screenSize[0] + SIZES["BackgroundTile"][0], screenSize[1] + SIZES["BackgroundTile"][1]))
for x in range(math.ceil(screenSize[0] / SIZES["BackgroundTile"][0]) + 1):
	for y in range(math.ceil(screenSize[1] / SIZES["BackgroundTile"][1]) + 1):
		BACKGROUNDS["cobblestone"].blit(CobblestoneImage, (x * SIZES["BackgroundTile"][0], y * SIZES["BackgroundTile"][1]))

gray = (90, 90, 90)

backgroundPreviews = []
surf = pygame.Surface(SIZES["BackgroundPreview"])
surf.fill(gray)
backgroundPreviews.append(BackgroundPreview([surf], 0, 0, *SIZES["BackgroundPreview"], "Gray", tag = "gray"))
backgroundPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
backgroundPreviews[-1].rect.x = 20

backgroundPreviews.append(BackgroundPreview([pygame.transform.scale(CobblestoneImage, SIZES["BackgroundPreview"])], 0, 0, *SIZES["BackgroundPreview"], "Cobblestone", tag = "cobblestone"))
backgroundPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
backgroundPreviews[-1].rect.x = backgroundPreviews[-2].rect.right + 20
backgroundPreviews[-1].choosed = True

blockPreviews = []

blockPreviews.append(BackgroundPreview([pygame.transform.scale(GeneratorImage, SIZES["BackgroundPreview"])], 0, 0, *SIZES["BackgroundPreview"], "Generator", tag = "Generator"))
blockPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
blockPreviews[-1].rect.x = 20
blockPreviews[-1].choosed = True

blockPreviews.append(BackgroundPreview([pygame.transform.scale(LeverImage[0], SIZES["BackgroundPreview"]), pygame.transform.scale(LeverImage[1], SIZES["BackgroundPreview"])], 0, 0, *SIZES["BackgroundPreview"], "Lever", tag = "Lever"))
blockPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
blockPreviews[-1].rect.x = blockPreviews[-2].rect.right + 20

blockPreviews.append(BackgroundPreview([pygame.transform.scale(NotImage, SIZES["BackgroundPreview"])], 0, 0, *SIZES["BackgroundPreview"], "NOT Gate", tag = "Not"))
blockPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
blockPreviews[-1].rect.x = blockPreviews[-2].rect.right + 20

blockPreviews.append(BackgroundPreview([pygame.transform.scale(PGImage, SIZES["BackgroundPreview"])], 0, 0, *SIZES["BackgroundPreview"], "Pulse gen.", tag = "Pulse_gen"))
blockPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
blockPreviews[-1].rect.x = blockPreviews[-2].rect.right + 20

blockPreviews.append(BackgroundPreview([pygame.transform.scale(ORImage, SIZES["BackgroundPreview"])], 0, 0, *SIZES["BackgroundPreview"], "OR Gate", tag = "OR"))
blockPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
blockPreviews[-1].rect.x = blockPreviews[-2].rect.right + 20

blockPreviews.append(BackgroundPreview([pygame.transform.scale(LampImage[0], SIZES["BackgroundPreview"]), pygame.transform.scale(LampImage[1], SIZES["BackgroundPreview"])], 0, 0, *SIZES["BackgroundPreview"], "Lamp", tag = "Lamp"))
blockPreviews[-1].rect.centery = backgroundControl["SurfRect"].centery
blockPreviews[-1].rect.x = blockPreviews[-2].rect.right + 20

connecting = [False, {}]

current_level = 0
current_background = "cobblestone"
choosed_block = "Generator"

blockPreviews_anim_step = 0

ticks = 0

CameraSpeedMessage = Message(screenSize[0] // 2, 100, "Camera speed: 20/2x", 3, is_alive = False, mode="center")

socketTh = threading.Thread(target=socketThread)
socketTh.start()

def mouseOnUI():
	if ((backgroundControl["active"] == False and mPos[1] > backgroundControl["OpenBGCButton"].rect.top and mPos[1] < backgroundControl["OpenBGCButton"].rect.bottom and mPos[0] > backgroundControl["OpenBGCButton"].rect.left and mPos[0] < backgroundControl["OpenBGCButton"].rect.right and mPos[1] > BlockControl["openButton"].rect.top and mPos[1] < BlockControl["openButton"].rect.bottom and mPos[0] > BlockControl["openButton"].rect.left and mPos[0] < BlockControl["openButton"].rect.right) or (backgroundControl["active"] and mPos[1] > screenSize[1] - backgroundControlSettings["surfaceHeight"])):
		return True
	else: return False

while running:
	click = pygame.mouse.get_pressed()
	keys = pygame.key.get_pressed()
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			running = False
			connected = False
			exit()
		if event.type == pygame.MOUSEMOTION:
			mPos = event.pos
	if connected:
		pos = [(camera.rect.x + mPos[0]) // layoutCellSize, (camera.rect.y + mPos[1]) // layoutCellSize]
		if ticks % blockPreview_anim_speed == 0:
			blockPreviews_anim_step += 1
			if BlockControl["active"]:
				for pr in blockPreviews:
					pr.swapTexture()
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 2:
					camera.onEventClick(mPos)

				elif not mouseOnUI():
					if event.button == 3:
						canBePlaced = True
						current_block = None
						if len(ServerBlocks) > 0:
							for bl in ServerBlocks:
								if pos == bl["pos"] and current_level == bl["level"]:
									canBePlaced = False
									current_block = bl
									break
						block = {}
						if canBePlaced:
							if choosed_block == "Generator": block = { "type": "Generator", "pos": list(pos), "level": current_level, "out": True, "connections": [], "inputs": [], "is_connected": []}
							elif choosed_block == "Not": block = { "type": "Not", "pos": list(pos), "level": current_level, "out": False, "connections": [], "inputs": [False], "is_connected": [[False]] }
							elif choosed_block == "OR": block = { "type": "OR", "pos": list(pos), "level": current_level, "out": False, "connections": [], "inputs": [False, False, False], "is_connected": [[False], [False], [False]] }
							elif choosed_block == "Lever": block = { "type": "Lever", "pos": list(pos), "level": current_level, "out": False, "connections": [], "inputs": [], "is_connected": [] }
							elif choosed_block == "Lamp": block = { "type": "Lamp", "pos": list(pos), "level": current_level, "out": False, "connections": [], "inputs": [False, False, False, False], "is_connected": [[False], [False], [False], [False]] }
							newBlocks.append(block)
							ServerBlocks.append(block)
						else:
							if current_block["type"] == "Lever":
								current_block["out"] = not current_block["out"]
								updatedBlocks.append(current_block)
					elif event.button == 1:
						for bl in ServerBlocks:
							if pos == bl["pos"] and current_level == bl["level"]:
								if not (connecting[0] and bl["pos"] == connecting[1]["pos"] and bl["level"] == connecting[1]["level"]):
									ServerBlocks.remove(bl)
									deletedBlocks.append(bl)
								break
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f and not connecting[0]:
					if current_level < 100: current_level += 1
				elif event.key == pygame.K_v:
					if CAMERA_MOVING_SPEED < MAX_CAMERA_MOVING_SPEED:
						CAMERA_MOVING_SPEED += STEP_CAMERA_MOVING_SPEED
						if CAMERA_MOVING_SPEED > MAX_CAMERA_MOVING_SPEED:
							CAMERA_MOVING_SPEED = MAX_CAMERA_MOVING_SPEED
					if CAMERA_MOVING_MODIFIER < MAX_CAMERA_MOVING_MODIFIER:
						CAMERA_MOVING_MODIFIER += STEP_CAMERA_MOVING_MODIFIER
						if CAMERA_MOVING_MODIFIER > MAX_CAMERA_MOVING_MODIFIER:
							CAMERA_MOVING_MODIFIER = MAX_CAMERA_MOVING_MODIFIER
					CameraSpeedMessage.changeText("Camera speed: {}/{}x".format(str(round(CAMERA_MOVING_SPEED)), str(round(CAMERA_MOVING_MODIFIER, 2))))
					CameraSpeedMessage.is_alive = True
				elif event.key == pygame.K_b:
					if CAMERA_MOVING_SPEED > MIN_CAMERA_MOVING_SPEED:
						CAMERA_MOVING_SPEED -= STEP_CAMERA_MOVING_SPEED
						if CAMERA_MOVING_SPEED < MIN_CAMERA_MOVING_SPEED:
							CAMERA_MOVING_SPEED = MIN_CAMERA_MOVING_SPEED
					if CAMERA_MOVING_MODIFIER > MIN_CAMERA_MOVING_MODIFIER:
						CAMERA_MOVING_MODIFIER -= STEP_CAMERA_MOVING_MODIFIER
						if CAMERA_MOVING_MODIFIER < MIN_CAMERA_MOVING_MODIFIER:
							CAMERA_MOVING_MODIFIER = MIN_CAMERA_MOVING_MODIFIER
					CameraSpeedMessage.changeText("Camera speed: {}/{}x".format(str(round(CAMERA_MOVING_SPEED)), str(round(CAMERA_MOVING_MODIFIER, 2))))
					CameraSpeedMessage.is_alive = True
				elif event.key == pygame.K_g and not connecting[0]:
					if current_level > 0: current_level -= 1
				elif event.key == pygame.K_e:
					if not backgroundControl["active"]:
						backgroundControl["active"] = True
						BlockControl["active"] = True
						backgroundControl["openAnim"] = 0.5
					else:
						backgroundControl["active"] = False
						BlockControl["active"] = False
						backgroundControl["closeAnim"] = 1

				elif not mouseOnUI():
					if event.key == pygame.K_r:
						if not connecting[0]:
							for bl in ServerBlocks:
								if bl["pos"] == pos and bl["level"] == current_level and not bl["type"] == "Lamp":
									connecting[0] = True
									connecting[1] = bl
									break
						else: connecting = [False, {}]
					elif event.key == pygame.K_t:
						if connecting[0]:
							if connecting[1]["pos"] != pos:
								for bl in ServerBlocks:
									if bl["pos"] == pos and bl["level"] == current_level and not bl["type"] == "Generator" and not bl["type"] == "Lever":
										for bl2 in ServerBlocks:
											if bl2["pos"] == connecting[1]["pos"] and bl2["level"] == connecting[1]["level"]:
												for index, i in enumerate(bl["is_connected"]):
													if not i[0]:
														bl["is_connected"][index] = [True, {"pos": bl2["pos"], "level": bl2["level"]}, index]
														updatedBlocks.append(bl)
														bl2["connections"].append([{"pos": bl["pos"], "level": bl["level"]}, index])
														updatedBlocks.append(bl2)
														connecting[0] = False
														break
												break
										break
						else:
							if bl["pos"] == pos and bl["level"] == current_level:
								a = len(bl["is_connected"]) - 1
								for i in range(len(bl["is_connected"])):
									if bl["is_connected"][a - i][0]:
										for bl2 in ServerBlocks:
											if bl2["pos"] == bl["is_connected"][a - i][1]["pos"] and bl2["level"] == bl["is_connected"][a - i][1]["level"]:
												bl2["connections"].remove([{"pos": bl["pos"], "level": bl["level"]}, bl["is_connected"][a - i][2]])
												updatedBlocks.append(bl2)
												connecting = [True, bl2]
												break
										bl["is_connected"][a - i] = [False]
										updatedBlocks.append(bl)
										break




		camera.move(click, mPos, keys)

		if current_background != "gray":
			screen.blit(BACKGROUNDS[current_background], [-camera.rect.x % SIZES["BackgroundTile"][0] - SIZES["BackgroundTile"][0], -camera.rect.y % SIZES["BackgroundTile"][1] - SIZES["BackgroundTile"][1]])
		else:
			screen.fill(gray)

		for bl in ServerBlocks:
			if bl["level"] == current_level:
				if bl["type"] == "Generator":
					screen.blit(GeneratorImage, camera.renderPos([bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize]))
				elif bl["type"] == "Not":
					screen.blit(NotImage, camera.renderPos([bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize]))
				elif bl["type"] == "OR":
					screen.blit(ORImage, camera.renderPos([bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize]))
				elif bl["type"] == "Lever":
					if not bl["out"]: screen.blit(LeverImage[0], camera.renderPos([bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize]))
					else: screen.blit(LeverImage[1], camera.renderPos([bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize]))
				elif bl["type"] == "Lamp":
					if bl["inputs"][0] or bl["inputs"][1] or bl["inputs"][2] or bl["inputs"][3]:
						screen.blit(LampImage[1], camera.renderPos([bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize]))
					else:
						screen.blit(LampImage[0], camera.renderPos([bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize]))

				if len(bl["is_connected"]) > 0 and bl["is_connected"][0][0]:
					pygame.draw.line(screen, (10, 10, 10), camera.renderPos([bl["pos"][0] * layoutCellSize, (bl["pos"][1] + 0.5) * layoutCellSize]), camera.renderPos([(bl["is_connected"][0][1]["pos"][0] + 1) * layoutCellSize, (bl["is_connected"][0][1]["pos"][1] + 0.5) * layoutCellSize]), cableThickn)
				if len(bl["is_connected"]) > 1 and bl["is_connected"][1][0]:
					pygame.draw.line(screen, (10, 10, 10), camera.renderPos([(bl["pos"][0] + 0.5) * layoutCellSize, bl["pos"][1] * layoutCellSize]), camera.renderPos([(bl["is_connected"][1][1]["pos"][0] + 1) * layoutCellSize, (bl["is_connected"][1][1]["pos"][1] + 0.5) * layoutCellSize]), cableThickn)
				if len(bl["is_connected"]) > 2 and bl["is_connected"][2][0]:
					pygame.draw.line(screen, (10, 10, 10), camera.renderPos([(bl["pos"][0] + 0.5) * layoutCellSize, (bl["pos"][1] + 1) * layoutCellSize]), camera.renderPos([(bl["is_connected"][2][1]["pos"][0] + 1) * layoutCellSize, (bl["is_connected"][2][1]["pos"][1] + 0.5) * layoutCellSize]), cableThickn)
				if len(bl["is_connected"]) > 3 and bl["is_connected"][3][0]:
					pygame.draw.line(screen, (10, 10, 10), camera.renderPos([(bl["pos"][0] + 1) * layoutCellSize, (bl["pos"][1] + 0.5) * layoutCellSize]), camera.renderPos([(bl["is_connected"][3][1]["pos"][0] + 1) * layoutCellSize, (bl["is_connected"][3][1]["pos"][1] + 0.5) * layoutCellSize]), cableThickn)

		if connecting[0]:
			pygame.draw.line(screen, (10, 10, 10), camera.renderPos([(connecting[1]["pos"][0] + 1) * layoutCellSize, (connecting[1]["pos"][1] + 0.5) * layoutCellSize]), mPos, 4)
		if not mouseOnUI():
			noBlocks = True
			for bl in ServerBlocks:
				if bl["pos"] == pos and bl["level"] == current_level:
					surf = pygame.Surface((layoutCellSize, layoutCellSize))
					surf.fill((10, 10, 10))
					surf.set_alpha(blockInfoAlpha)
					text1 = mainFont.render("IN: "+str(bl["inputs"]).replace("False", "0").replace("True", "1"), FONTaa, (255, 255, 255))
					text2 = mainFont.render("OUT: "+str(bl["out"]).replace("False", "0").replace("True", "1"), FONTaa, (255, 255, 255))
					rect1 = text1.get_rect(centerx = bl["pos"][0] * layoutCellSize + layoutCellSize // 2)
					rect2 = text2.get_rect(centerx = bl["pos"][0] * layoutCellSize + layoutCellSize // 2)
					rect1.bottom = bl["pos"][1] * layoutCellSize + layoutCellSize // 2
					rect2.top = rect1.bottom
					noBlocks = False
					break
			color = layoutColor1 if noBlocks else layoutColor2
			pygame.draw.rect(screen, color, camera.renderRect(pygame.Rect(pos[0] * layoutCellSize, pos[1] * layoutCellSize, layoutCellSize, layoutCellSize)), layoutThickn)
			if not noBlocks:
				screen.blit(surf, camera.renderPos([pos[0] * layoutCellSize, pos[1] * layoutCellSize]))
				screen.blit(text1, camera.renderRect(rect1))
				screen.blit(text2, camera.renderRect(rect2))


		for i in PlayersData:
			if i["level"] == current_level:
				pos2 = camera.renderPos(i["mPos"])
				if camera.checkVPos(pos2): pygame.draw.circle(screen, Cursors["other"]["color"], pos2, Cursors["other"]["radius"])
				text = mainFont.render(i["nickname"], FONTaa, Cursors["other"]["textColor"])
				textSize = text.get_size()
				surf = pygame.Surface(textSize)
				surf.set_alpha(Cursors["other"]["textBackgroundAlpha"])
				surf.fill((0, 0, 0))
				textRect = text.get_rect(center = (pos2[0], pos2[1] - 27))
				if camera.checkVisible(textRect):
					screen.blit(surf, textRect)
					screen.blit(text, textRect)
				if not camera.checkVPos(pos2):
					try:
						x2, y2 = i["mPos"]
						x1, y1 = screenSize[0] // 2, screenSize[1] // 2
						angle = math.atan( (y2 - y1) / (x2 - x1) )
						if x2 > x1: angle += math.pi
					except ZeroDivisionError: angle = 0
					x3, y3 = int(x1 - (y1 - 16) * math.cos(angle)), int(y1 - (y1 - 16) * math.sin(angle))
					img = pygame.transform.rotate(PlayerIndicatorImage, -math.degrees(angle))
					rect = img.get_rect(center=[x3,y3])
					screen.blit(img, rect)

		if backgroundControl["active"]:
			for event in events:
				if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
					backgroundControl["CloseBGCButton"].on_MOUSEBUTTONUP(mPos)
					if not BlockControl["active"]:
						for pr in backgroundPreviews:
							pr.on_MOUSEBUTTONUP(mPos)
							if pr.choosed:
								current_background = pr.tag
								for pr2 in backgroundPreviews:
									if pr2 != pr: pr2.choosed = False
					else:
						for pr in blockPreviews:
							pr.on_MOUSEBUTTONUP(mPos)
							if pr.choosed:
								choosed_block = pr.tag
								for pr2 in blockPreviews:
									if pr2 != pr: pr2.choosed = False

			backgroundControl["CloseBGCButton"].update(mPos, click[0])
			if backgroundControl["CloseBGCButton"].eventTrigger():
				backgroundControl["active"] = False
				BlockControl["active"] = False
				backgroundControl["closeAnim"] = 1
			if backgroundControl["openAnim"] > 0:
				anim = backgroundControlSettings["surfaceHeight"] * backgroundControl["openAnim"]
				screen.blit(backgroundControl["BackgroundImage"], (0, backgroundControl["SurfRect"].top + anim))
				screen.blit(backgroundControl["CloseBGCButton"].image, (backgroundControl["CloseBGCButton"].rect.x, backgroundControl["CloseBGCButton"].rect.y + anim))
				screen.blit(backgroundControl["CloseBGCButton"].text, (backgroundControl["CloseBGCButton"].text_rect.x, backgroundControl["CloseBGCButton"].text_rect.y + anim))
				backgroundControl["openAnim"] -= 0.15
			else:
				screen.blit(backgroundControl["BackgroundImage"], backgroundControl["SurfRect"])
				if not BlockControl["active"]:
					for pr in backgroundPreviews: pr.draw(screen)
				else:
					for pr in blockPreviews:
						pr.draw(screen)
				backgroundControl["CloseBGCButton"].draw(screen)

		else:
			for event in events:
				if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
					backgroundControl["OpenBGCButton"].on_MOUSEBUTTONUP(mPos)
					BlockControl["openButton"].on_MOUSEBUTTONUP(mPos)

			backgroundControl["OpenBGCButton"].update(mPos, click[0])
			BlockControl["openButton"].update(mPos, click[0])
			if backgroundControl["OpenBGCButton"].eventTrigger():
				backgroundControl["active"] = True
				backgroundControl["openAnim"] = 1
			elif BlockControl["openButton"].eventTrigger():
				backgroundControl["active"] = True
				backgroundControl["openAnim"] = 1
				BlockControl["active"] = True

			if backgroundControl["closeAnim"] > 0:
				anim = backgroundControlSettings["surfaceHeight"] * (1 - backgroundControl["closeAnim"])
				screen.blit(backgroundControl["BackgroundImage"], (0, backgroundControl["SurfRect"].top + anim))
				screen.blit(backgroundControl["CloseBGCButton"].image, (backgroundControl["CloseBGCButton"].rect.x, backgroundControl["CloseBGCButton"].rect.y + anim))
				screen.blit(backgroundControl["CloseBGCButton"].text, (backgroundControl["CloseBGCButton"].text_rect.x, backgroundControl["CloseBGCButton"].text_rect.y + anim))
				backgroundControl["closeAnim"] -= 0.20
			else:
				backgroundControl["OpenBGCButton"].draw(screen)
				BlockControl["openButton"].draw(screen)
		text = FONT3.render("Floor: "+str(current_level), FONTaa, (255, 255, 255))
		screen.blit(text, (screenSize[0] // 2 - text.get_size()[0] // 2, 15))
		CameraSpeedMessage.draw(screen)

	else:
		text = FONT3.render("Lost connection or server closed", FONTaa, (180, 180, 180))
		rect = text.get_rect(center=[screenSize[0] // 2, screenSize[1] // 2])
		CloseButton.update(mPos, click[0])
		if CloseButton.state == 2:
			pygame.quit()
			running = False
			connected = False
			exit()
		screen.fill((20, 20, 20))
		screen.blit(text, rect)
		CloseButton.draw(screen)
	pygame.draw.circle(screen, Cursors["self"]["color"], mPos, Cursors["self"]["radius"])
	pygame.display.flip()
	clock.tick(60)
	ticks += 1
