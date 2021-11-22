import pygame
import os
import time
import random
from pygame import mixer
pygame.font.init()

pygame.init()

WIDTH, HEIGHT=1080,1920
TELA=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Invasão do Espaço")

NAVE_VERMELHA=pygame.image.load(os.path.join("img","nave_vermelha.png"))
NAVE_VERDE=pygame.image.load(os.path.join("img","nave_verde.png"))
NAVE_AMARELA=pygame.image.load(os.path.join("img","nave_amarela.png"))
NAVE_AZUL=pygame.image.load(os.path.join("img","nave_azul.png"))

LASER_VERMELHO=pygame.image.load(os.path.join("img","laser_vermelho.png"))
LASER_VERDE=pygame.image.load(os.path.join("img","laser_verde.png"))
LASER_AMARELO=pygame.image.load(os.path.join("img","laser_amarelo.png"))
LASER_AZUL=pygame.image.load(os.path.join("img","laser_azul.png"))

FUNDO=pygame.transform.scale(pygame.image.load(os.path.join("img","espaco.png")), (WIDTH,HEIGHT))

pygame.mixer.music.load(os.path.join("som","background.wav"))
pygame.mixer.music.play(-1)
fogo=pygame.mixer.Sound('som/fogo.wav')
boom=pygame.mixer.Sound('som/boom.wav')

class Laser:
	def __init__(self, x, y, img):
		self.x=x
		self.y=y 
		self.img=img
		self.mask=pygame.mask.from_surface(self.img)

	def draw(self,window):
		window.blit(self.img,(self.x, self.y))

	def move(self, vel):
		self.y+=vel

	def off_screen(self, height):
		return not(self.y<=height and self.y>=0)

	def collision(self,obj):
		return collide(self,obj)

class Nave:
	COOLDOWN=30

	def __init__(self,x,y,health=100):
		self.x=x
		self.y=y
		self.health=health
		self.nave_img=None
		self.laser_img=None
		self.lasers=[]
		self.cool_down_counter=0

	def draw(self, window):
		window.blit(self.nave_img,(self.x,self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self,vel,obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health-=10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter>=self.COOLDOWN:
			self.cool_down_counter=0
		elif self.cool_down_counter>0:
			self.cool_down_counter+=1

	def shoot(self):
		if self.cool_down_counter==0:
			laser=Laser(self.x,self.y,self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter=1

	def get_width(self):
		return self.nave_img.get_width()

	def get_height(self):
		return self.nave_img.get_height()

class Player(Nave):
	def __init__(self,x,y,health=100):
		super().__init__(x,y,health)
		self.nave_img=NAVE_AZUL
		self.laser_img=LASER_AZUL
		self.mask=pygame.mask.from_surface(self.nave_img)
		self.max_health=health

	def move_lasers(self,vel,objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)
							boom.play()

	def draw(self,window):
		super().draw(window)
		self.healthbar(window)

	def healthbar(self,window):
		pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.nave_img.get_height()+10,self.nave_img.get_width(),10))
		pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.nave_img.get_height()+10,self.nave_img.get_width()*(self.health/self.max_health), 10))

class Inimigo(Nave):
	COLOR_MAP=	{
				"red":(NAVE_VERMELHA,LASER_VERMELHO),
				"green":(NAVE_VERDE,LASER_VERDE),
				"yellow":(NAVE_AMARELA, LASER_AMARELO)
				}

	def __init__(self,x,y,color,health=100):
		super().__init__(x,y,health)
		self.nave_img,self.laser_img=self.COLOR_MAP[color]
		self.mask=pygame.mask.from_surface(self.nave_img)

	def move(self,vel):
		self.y+=vel

	def shoot(self):
		if self.cool_down_counter==0:
			laser=Laser(self.x-20,self.y,self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter=1
			fogo.play()

def collide(obj1,obj2):
	offset_x=obj2.x-obj1.x
	offset_y=obj2.y-obj1.y
	return obj1.mask.overlap(obj2.mask,(offset_x,offset_y))!=None

def main():
	run=True
	FPS=60
	level=0
	lives=5
	main_font=pygame.font.SysFont("verdana",40)
	lost_font=pygame.font.SysFont("verdana",50)

	inimigos=[]
	wave_length=5
	inimigo_vel=1

	player_vel=5
	laser_vel=5

	player=Player(300,630)

	clock=pygame.time.Clock()

	lost=False
	lost_count=0

	def redraw_window():
		TELA.blit(FUNDO,(0,0))
		lives_label=main_font.render(f"Vidas: {lives}",1,(255,255,255))
		level_label=main_font.render(f"Nível: {level}",1,(255,255,255))

		TELA.blit(lives_label,(10,10))
		TELA.blit(level_label,(WIDTH-level_label.get_width()-10,10))

		for inimigo in inimigos:
			inimigo.draw(TELA)

		player.draw(TELA)

		if lost:
			lost_label=lost_font.render("Você Perdeu!",1,(255,255,255))
			TELA.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,350))

		pygame.display.update()

	while run:
		clock.tick(FPS)
		redraw_window()

		if lives<=0 or player.health<=0:
			lost=True
			lost_count+=1

		if lost:
			if lost_count>FPS*3:
				run=False
			else:
				continue

		if len(inimigos)==0:
			level+=1
			wave_length+=5
			for i in range(wave_length):
				inimigo=Inimigo(random.randrange(50,WIDTH-100), random.randrange(-1500,-100),random.choice(["red","green","yellow"]))
				inimigos.append(inimigo)

		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				run=False
				pygame.quit()
				quit()

		keys=pygame.key.get_pressed()
		if keys[pygame.K_LEFT] and player.x-player_vel>0:
			player.x-=player_vel
		if keys[pygame.K_RIGHT] and player.x+player_vel+player.get_width()<WIDTH:
			player.x+=player_vel
		if keys[pygame.K_UP] and player.y-player_vel>0:
			player.y-=player_vel
		if keys[pygame.K_DOWN] and player.y+player_vel+player.get_height()+15<HEIGHT:
			player.y+=player_vel
		if keys[pygame.K_SPACE]:
			fogo.play()
			player.shoot()

		for inimigo in inimigos[:]:
			inimigo.move(inimigo_vel)
			inimigo.move_lasers(laser_vel,player)

			if random.randrange(0,2*60)==1:
				inimigo.shoot()

			if collide(inimigo,player):
				player.health-=10
				inimigos.remove(inimigo)
				boom.play()
			elif inimigo.y+inimigo.get_height()>HEIGHT:
				lives-=1
				inimigos.remove(inimigo)

		player.move_lasers(-laser_vel,inimigos)

def main_menu():
	title_font=pygame.font.SysFont("verdana",70)
	run=True
	while run:
		TELA.blit(FUNDO,(0,0))
		title_label=title_font.render("Clique na tela para começar",1,(255,255,255))
		TELA.blit(title_label,(WIDTH/2-title_label.get_width()/2,350))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				run=False
			if event.type==pygame.MOUSEBUTTONDOWN:
				main()
	pygame.quit()

main_menu()



