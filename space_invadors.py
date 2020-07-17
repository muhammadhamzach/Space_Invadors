import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time
import random
from pygame import mixer

pygame.init()
FPS = 60

WIDTH, HEIGHT = 750, 650
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invadors (kinda xD)")

#ships
RED_SPACE_SHIP = pygame.image.load("assets\pixel_ship_red_small.png")
GREEN_SPACE_SHIP = pygame.image.load("assets\pixel_ship_green_small.png")
BLUE_SPACE_SHIP = pygame.image.load("assets\pixel_ship_blue_small.png")
YELLOW_SPACE_SHIP = pygame.image.load("assets\pixel_ship_yellow.png")
#laser
RED_LASER = pygame.image.load("assets\pixel_laser_red.png")
GREEN_LASER = pygame.image.load("assets\pixel_laser_green.png")
BLUE_LASER = pygame.image.load("assets\pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load("assets\pixel_laser_yellow.png")
#bvackground
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")),(WIDTH,HEIGHT))
#fonts
main_font = pygame.font.SysFont("comicsans", 50)
lost_font = pygame.font.SysFont("comicsans", 60)
#background music
mixer.music.load(os.path.join("assets", "background.wav"))
mixer.music.play(-1)

level = 0
lives = 3
lost = False

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, win):
        win.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel
    
    def off_screen(self):
        return not(self.y <= HEIGHT and self.y > 0)
    
    def collision(self, obj):
        return collide(self, obj)
    
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class Ship:
    COOLDOWN = 30 
    
    def __init__(self,x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, win):
        win.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(win)
    
    def move_lasers(self, vel, obj, score):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 25
                score -= 1
                self.lasers.remove(laser)
        return score
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
        
class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        
    def move_lasers(self, vel, objs, score):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        score += level
                        explosion_sound = mixer.Sound(os.path.join("assets", "explosion.wav"))
                        explosion_sound.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
        return score                    
        
    def healthbar(self, win):
        pygame.draw.rect(win, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(win, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))    
        
    def draw(self, win):
        super().draw(win)
        self.healthbar(win)
              
class Enemy(Ship):
    COLOR_MAP = {
            "red": (RED_SPACE_SHIP, RED_LASER),
            "green": (GREEN_SPACE_SHIP, GREEN_LASER),
            "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }
    
    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def redraw_window(player, enemies):
        win.blit(BG,(0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))
        win.blit(lives_label, (10,10))
        win.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        win.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 10))
        
        for enemy in enemies:
            enemy.draw(win)            
        player.draw(win)
        
        if lost: 
            win.blit(BG,(0,0))
            lost_label = lost_font.render("Game Over!", 1, (255,255,255))
            score_label = main_font.render(f" Your Score: {score}", 1, (255,255,255))
            win.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2 -50)) 
            win.blit(score_label, (WIDTH/2 - score_label.get_width()/2, HEIGHT/2))
            
        pygame.display.update()

def game():
    run = True
    global level, lives, lost, score
    clock = pygame.time.Clock()
    lost_count = 0                      #counting time of game over message
    score = 0                           #initial score
    player_val = 5                      #ship speed
    laser_vel = 5                       #laser speed
    player = Player(350,500)            #player starting position
    
    wave_length = 5                     #initial number of enemies
    enemy_vel = 1                       #velocity of enemies
    enemies = []

    while run:
        clock.tick(FPS)
        redraw_window(player, enemies)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        if lives == 0:
                lost = True
                lost_count +=1
        if player.health <= 0:
                lives -= 1
                player.health = 100
        
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            if level > 1:
                wave_length += 3
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_val > 0:      #left
            player.x -= player_val
        if keys[pygame.K_RIGHT] and player.x + player_val + player.get_width() < WIDTH:     #right
            player.x += player_val
        if keys[pygame.K_UP] and player.y - player_val > 0:        #up
            player.y -= player_val
        if keys[pygame.K_DOWN] and player.y + player_val + player.get_height() + 15 < HEIGHT:      #down
            player.y += player_val
        if keys[pygame.K_SPACE]:
            player.shoot()
            laser_sound = mixer.Sound(os.path.join("assets", "laser.wav"))
            laser_sound.play()
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            score = enemy.move_lasers(laser_vel, player, score)
            
            if random.randrange(0, 3*FPS) == 1:
                enemy.shoot()
            
            if collide (enemy, player):
                player.health -= 50
                enemies.remove(enemy)
                score -= level
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                score -= level
                enemies.remove(enemy)    
                
        score = player.move_lasers(-laser_vel, enemies, score)
        
def main():
    run = True
    game_font = pygame.font.SysFont("comicsans", 80)
    title_font = pygame.font.SysFont("comicsans", 40)
    
    while run:
        global lives
        win.blit(BG, (0,0))
        game_label = game_font.render("Space Invadors!", 1, (255,255,255))
        title_label = title_font.render("Press any key to begin...", 1, (255,255,255))
        win.blit(game_label, (WIDTH/2 - game_label.get_width()/2, HEIGHT/2 - 100))
        win.blit(title_label, (WIDTH/2 - title_label.get_width()/2, HEIGHT/2 + 60))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                game()
    pygame.quit()
            
main()