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

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 128, size , size) # load diff terrain, find coord of top left corner 
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)
            
 # use sprite for pixel perfect collision
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0) 
    GRAVITY = 1 
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
     # account for delay in changing sprite
    ANIMATION_DELAY = 3
    
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0 # air time to increment velocity
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0 
        
    def jump(self):
        self.y_vel = -self.GRAVITY * 8 # 8 is speed of jump
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
           
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
    def been_hit(self):
        self.hit = True
        self.hit_count = 0
        
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
    
    # be called once every frame, move character in right direction and update animation 
    # increase y velocity by gravity, adjust in terms of how long we have been falling for
    # picks up pace with every tile 
    
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        
        self.fall_count += 1
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
            
        self.update_sprite()
        
    def landed(self):
        self.fall_count = 0 
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1 # bounce away when hit head
    
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.jump_count > 0:
            if self.y_vel != 0:
                if self.jump_count == 1:
                    sprite_sheet = "jump"
                elif self.jump_count == 2:
                    sprite_sheet = "double_jump"
            elif self.y_vel > self.GRAVITY*2: 
                sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
         # every 5 frames, want to show diff sprite in whatever animation we are using
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
     # update rect that holds sprite according to diff sizes 
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
         # mapping of pixels within sprite; allows pixel perfection collision
        self.mask = pygame.mask.from_surface(self.sprite)
        
    def draw(self, wind, offset_x):
        wind.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Objects(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA) # supports trnasparent images 
        self.width = width
        self.height = height 
        self.name = name
        
    def draw(self, wind, offset_x):
        wind.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Objects):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)
        
class Fire(Objects):
    ANIMATION_DELAY = 3
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
        
    def on(self):
        self.animation_name = "on"
    def off(self):
        self.animation_name = "off"
    
    def loop(self):
        sprites = self.fire[self.animation_name]
         # every 5 frames, want to show diff sprite in whatever animation we are using
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
         # update method
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
         # since fire static, we need to reset animation count that can lag program 
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
    
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

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj): # tell me if i am colliding w object
            if dy > 0:
                player.rect.bottom = obj.rect.top # set feet equal to top of block
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom # set head equal to top of block (COLLIDE NOT THROUGH)
                player.hit_head()
                
            collided_objects.append(obj)   
    return collided_objects
 
 # first check that if u hit on L or R it doesnt think its the top 
def collide(player, objects, dx):
     # preemitly moving player to where they would be if moving L or R 
    player.move(dx, 0)
    player.update()
    collided_objects = None
    
     # checking if collided 
    for obj in objects: 
        if pygame.sprite.collide_mask(player, obj):
            collided_objects = obj
            break 
     # reverse movement 
    player.move(-dx, 0)
    player.update()
    return collided_objects
    

def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL*2)
    collide_right = collide(player, objects, PLAYER_VEL*2
                            )
     # check if we are able to move left or right, move if no collision
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
        
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check: 
        if obj and obj.name == "fire":
            player.been_hit()
 
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background: 
        window.blit(bg_image, tile) # draw background image into this tile position 
    
    for obj in objects:
        obj.draw(window, offset_x)
        
    player.draw(window, offset_x)
        
    pygame.display.update() 
 
 # includes event loop 
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink2.png")
    
    block_size = 96
    player = Player(100, 100, 50, 50)
    LEVEL_LENGTH = 200 # blocks 
     # create blocks that go to left and right of screen
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-10, LEVEL_LENGTH)] 
            # for i in range(-WIDTH // block_size, WIDTH*2 // block_size)]
     # asterisk breaks all elements in floor in objects var
    objects = [*floor, Block(0, HEIGHT - block_size*2, block_size), 
               Block(block_size*3, HEIGHT - block_size*4, block_size),
               fire]
    offset_x = 0
    scroll_area_width = 280 # start scrolling when 200 pixels to L or R 
    
    run = True 
    while run: 
        clock.tick(FPS) # ensure while look runs 60 fps, regulation across any device 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        
        player.loop(FPS) # what moves player
        fire.loop()
        handle_move(player, objects)
        draw(window,background,bg_image, player, objects, offset_x)
         
         # explanation? 
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0)):
            offset_x += player.x_vel
    
    pygame.quit()
    quit()
                          
if __name__ == "__main__":
    main(window)