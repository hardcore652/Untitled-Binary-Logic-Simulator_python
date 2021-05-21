import pygame, time
import socket, threading, json
import os, copy, sys, math
from gameSettings import *

pygame.init()

dirname = os.path.dirname(__file__)

mainFont = pygame.font.SysFont("Verdana", mainFontSize)

clock = pygame.time.Clock()

class Camera:
	def __init__(self):
		self.rect = pygame.Rect(0, 0, *screenSize)
		self.dragPos = [0, 0]
		self.startRectPos = self.rect.topleft
	def move(self, click, mousePos):
		if click[1]:
			self.rect.x = self.startRectPos[0] - (mousePos[0] - self.dragPos[0]) * CAMERA_MOVING_MODIFIER
			self.rect.y = self.startRectPos[1] - (mousePos[1] - self.dragPos[1]) * CAMERA_MOVING_MODIFIER
	def onEventClick(self, mousePos):
		self.dragPos = mousePos
		print(self.dragPos)
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
		self.text = font.render(text, True, self.text_color)
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


screen = pygame.display.set_mode((1280, 720))
screenSize = screen.get_size()

clientSocket = socket.socket()

del ip
CloseButton = Button(screenSize[0] // 2 - 15, screenSize[1] // 2 + 25, 100, 50, "Close", color=(160, 100, 100), font=pygame.font.SysFont("Verdana", 25), tag="close", mode="topright")
RetryButton = Button(screenSize[0] // 2 + 15, screenSize[1] // 2 + 25, 100, 50, "Retry", font=pygame.font.SysFont("Verdana", 25), tag="retry", mode="topleft")

running = True

mPos = [0, 0]
camera = Camera()
while running:
	try:
		screen.fill((20, 20, 20))
		font = pygame.font.SysFont("Verdana", 30)
		text = font.render("Connecting...", 1, (180, 180, 180))
		rect = text.get_rect(center=[screenSize[0] // 2, screenSize[1] // 2])
		screen.blit(text, rect)
		pygame.display.flip()
		clientSocket.connect(address)
		clientSocket.settimeout(15)
		clientSocket.send(nick.encode())
		break
	except:
		try:
			font = pygame.font.SysFont("Verdana", 30)
			text = font.render("Failed to connect to {}:{}".format(str(address[0]), str(address[1])), 1, (180, 180, 180))
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
	global clientSocket, running, connected, mPos, PlayersData, newBlocks, deletedBlocks, ServerBlocks
		
	while running:
		try:
			data = {"mPos": [mPos[0] + camera.rect.x, mPos[1] + camera.rect.y], "newBlocks":newBlocks, "deletedBlocks": deletedBlocks}
			newBlocks = []
			deletedBlocks = []
			clientSocket.send(json.dumps(data).encode())
			recieved = clientSocket.recv(8192).decode("utf-8")
			if not recieved: running = False
			recieved = json.loads(recieved)
			PlayersData = recieved["PlayersData"]
			for bl in recieved["updatedBlocks"]:
				for bl2 in ServerBlocks:
					if bl["pos"] == bl2["pos"]:
						bl2 = bl
			for bl in recieved["newBlocks"]:
				ServerBlocks.append(bl)
			for bl in recieved["deletedBlocks"]:
				for bl2 in ServerBlocks:
					if bl["pos"] == bl2["pos"]:
						ServerBlocks.remove(bl)

		except:
			CloseButton.rect.centerx = screenSize[0] // 2
			CloseButton.text_rect.centerx = screenSize[0] // 2
			connected = False
			break
PlayersData = []
newBlocks = []
deletedBlocks = []
ServerBlocks = []
socketTh = threading.Thread(target=socketThread)
socketTh.start()
pygame.mouse.set_visible(False)
backgroundControl = {}
backgroundControl["active"] = False
backgroundControl["CloseBGCButton"] = Button(screenSize[0], screenSize[1] - backgroundControlSettings["surfaceHeight"], 35, 35, "X", text_color=(10, 10, 10), color=(160, 0, 0), font=mainFont, tag="BGSclose", mode="topright")
backgroundControl["OpenBGCButton"] = Button(screenSize[0] - 5, screenSize[1] - 5, 117, 45, "Backgrounds", text_color=(10, 10, 10), color=(160, 160, 0), font=mainFont, tag="BGS", mode="bottomright")
backgroundControl["surface"] = pygame.Surface((screenSize[0], backgroundControlSettings["surfaceHeight"]))
backgroundControl["surface"].fill(backgroundControlSettings["surfaceFillColor"])



while running:
	click = pygame.mouse.get_pressed()
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
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 2:
					camera.onEventClick(mPos)
				elif not ((backgroundControl["active"] == False and mPos[1] > backgroundControl["OpenBGCButton"].rect.top and mPos[1] < backgroundControl["OpenBGCButton"].rect.bottom and mPos[0] > backgroundControl["OpenBGCButton"].rect.left and mPos[0] < backgroundControl["OpenBGCButton"].rect.right) or (backgroundControl["active"] and mPos[1] > screenSize[1] - backgroundControlSettings["surfaceHeight"])):
					if event.button == 3:
						if not list(pos) in [list(bl["pos"]) for bl in ServerBlocks]:
							newBlocks.append({"type":"Cable", "pos":pos})
					elif event.button == 1:
						if list(pos) in [list(bl["pos"]) for bl in ServerBlocks]:
							for bl in ServerBlocks:
								if list(bl["pos"]) == list(pos):
									deletedBlocks.append(bl)
		camera.move(click, mPos)
		pos = ((camera.rect.x + mPos[0]) // layoutCellSize, (camera.rect.y + mPos[1]) // layoutCellSize)

		screen.fill((120, 120, 120))

		try:
			x2, y2 = mPos
			x1, y1 = screenSize[0] // 2, screenSize[1] // 2
			angle = math.atan( (y2 - y1) / (x2 - x1) )
			if x2 > x1: angle += math.pi
			#angle = math.degrees(angle)
			print(angle)
			print(x1 - x1 * math.cos(angle), y1 - y1 * math.sin(angle))
		except ZeroDivisionError: print(0)

		for bl in ServerBlocks:
			if bl["type"] == "Cable":
				rect = camera.renderRect(pygame.Rect(bl["pos"][0] * layoutCellSize, bl["pos"][1] * layoutCellSize, layoutCellSize, layoutCellSize))
				if camera.checkVisible(rect):
					pygame.draw.rect(screen, (255, 255, 255), rect)
		if not ((backgroundControl["active"] == False and mPos[1] > backgroundControl["OpenBGCButton"].rect.top and mPos[1] < backgroundControl["OpenBGCButton"].rect.bottom and mPos[0] > backgroundControl["OpenBGCButton"].rect.left and mPos[0] < backgroundControl["OpenBGCButton"].rect.right) or (backgroundControl["active"] and mPos[1] > screenSize[1] - backgroundControlSettings["surfaceHeight"])):
			color = layoutColor1 if not list(pos) in [list(bl["pos"]) for bl in ServerBlocks] else layoutColor2
			pygame.draw.rect(screen, color, camera.renderRect(pygame.Rect(pos[0] * layoutCellSize, pos[1] * layoutCellSize, layoutCellSize, layoutCellSize)), layoutThickn)


		for i in PlayersData:
			pos2 = camera.renderPos(i["mPos"])
			if camera.checkVPos(pos2): pygame.draw.circle(screen, Cursors["other"]["color"], pos2, Cursors["other"]["radius"])
			text = mainFont.render(i["nickname"], True, Cursors["other"]["textColor"])
			textSize = text.get_size()
			surf = pygame.Surface(textSize)
			surf.set_alpha(Cursors["other"]["textBackgroundAlpha"])
			surf.fill((0, 0, 0))
			textRect = text.get_rect(center = (pos2[0], pos2[1] - 27))
			if camera.checkVisible(textRect):
				screen.blit(surf, textRect)
				screen.blit(text, textRect)
		if backgroundControl["active"]:
			for event in events:
				if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
					backgroundControl["CloseBGCButton"].on_MOUSEBUTTONUP(mPos)

			backgroundControl["CloseBGCButton"].update(mPos, click)
			if backgroundControl["CloseBGCButton"].eventTrigger():
				backgroundControl["active"] = False
			
			screen.blit(backgroundControl["surface"], (0, screenSize[1] - backgroundControl["surface"].get_size()[1]))
			backgroundControl["CloseBGCButton"].draw(screen)
		else:
			for event in events:
				if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
					backgroundControl["OpenBGCButton"].on_MOUSEBUTTONUP(mPos)

			backgroundControl["OpenBGCButton"].update(mPos, click)
			if backgroundControl["OpenBGCButton"].eventTrigger():
				backgroundControl["active"] = True

			backgroundControl["OpenBGCButton"].draw(screen)

	else:
		font = pygame.font.SysFont("Verdana", 30)
		text = font.render("Lost connection or server closed", 1, (180, 180, 180))
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
