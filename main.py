import os 
import random
import math 
import pygame 
 # use os so dynamically loading sprite sheets and images 
from os import listdir
from os.path import isfile, join 

 # initialize pygame module 
pygame.init()

 # set caption 
pygame.display.set_caption("python game")

 # background default - BG_COLOR = (255,255,255) # white RGB
 # adjust depending on size of computer screen 
WIDTH, HEIGHT = 800, 700
 # frames per sec
FPS = 60
 # speed which player moves 
PLAYER_VEL = 5

 # create window
window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))] # load every single file in this dir
    
    all_sprites = {}
    
    for image in images: 
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()
        sprites = []
        
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            # create surface that is size of our desired individual animation frame 
            # grab image, draw it on surface and export it 
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface)) # double image size
        
         # multidrectional animation, moving right AND left
        if direction: 
            all_sprites[image.replace(".png", "") + "_right"] = sprites # strip png and append right
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites) # strip png and append left
        else: 
            all_sprites[image.replace(".png", "")] = sprites
        
    return all_sprites
            
 # use sprite for pixel perfect collision
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0) 
    GRAVITY = 1 
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0 # air time to increment velocity
           
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
        
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    #be called once every frame, move character in right direction and update animation 
    # increase y velociy by gravity, adjust in terms of how long we have been falling for
    # picks up pace with every tile 
    
    def loop(self, fps):
        # self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        
        self.fall_count += 1
    
    def draw(self, wind):
        self.sprite = self.SPRITES["idle_" + self.direction][0]
        wind.blit(self.sprite, (self.rect.x, self.rect.y))
    
        
 # return list of all background tiles
 # run from directory the file exists in (MAKE SURE CORRECT DIRECTORY)
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = [] 
    
    for i in range(WIDTH // width+1): # screen // width of tile, add 1 to make sure no gaps 
        for j in range(HEIGHT // height+1):
            pos = (i * width, j * height) # start in top left hand corner of the tile im currently adding color
            tiles.append(pos) # (x,y)
    
    return tiles, image 

def handle_move(player):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)
        
def draw(window, background, bg_image, player):
    for tile in background: 
        window.blit(bg_image, tile) # draw background image into this tile position 
    
    player.draw(window)
        
    pygame.display.update() 
 
 # includes event loop 
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")
    
    player = Player(100, 100, 50, 50)
    
    run = True 
    while run: 
        clock.tick(FPS) # ensure while look runs 60 fps, regulation across any device 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        player.loop(FPS) # what moves player
        handle_move(player)
        draw(window,background,bg_image, player)
    
    pygame.quit()
    quit()
                          
if __name__ == "__main__":
    main(window)