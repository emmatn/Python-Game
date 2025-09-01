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
 
 # use sprite for pixel perfect collision
class Player(pygame.sprite.Sprite):
    
    

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

def draw(window, background, bg_image):
    for tile in background: 
        window.blit(bg_image, tile) # draw background image into this tile position 
        
    pygame.display.update() 
 
 # includes event loop 
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")
    
    run = True 
    while run: 
        clock.tick(FPS) # ensure while look runs 60 fps, regulation across any device 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        draw(window,background,bg_image)
    
    pygame.quit()
    quit()
                
            
if __name__ == "__main__":
    main(window)