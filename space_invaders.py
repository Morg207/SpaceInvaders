import pygame
import random

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 650
WINDOW = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.mouse.set_visible(False)
pygame.mixer.music.load("music/grey sector.mp3")
pygame.mixer.music.play(loops=-1)
pygame.display.set_caption("Space Invaders")
window_icon = pygame.image.load("images/window icon.png").convert_alpha()
window_icon = pygame.transform.scale(window_icon,(32,32))
pygame.display.set_icon(window_icon)
BACKGROUND_COLOUR = (70,70,70)
CLOCK = pygame.time.Clock()
FPS = 60
PLAYER_IMAGE = pygame.image.load("images/player.png").convert_alpha()
PLAYER_RECT = PLAYER_IMAGE.get_rect()
PLAYER_RECT.center = (WINDOW_WIDTH/2,WINDOW_HEIGHT-18)
LASER_SOUND = pygame.mixer.Sound("sounds/laser.ogg")
EXPLOSION_SOUND = pygame.mixer.Sound("sounds/explosion.wav")
RED_INVADER_IMAGE = pygame.image.load("images/red invader.png").convert_alpha()
GREEN_INVADER_IMAGE = pygame.image.load("images/green invader.png").convert_alpha()
YELLOW_INVADER_IMAGE = pygame.image.load("images/yellow invader.png").convert_alpha()
MYSTERY_IMAGE = pygame.image.load("images/mystery ship.png").convert_alpha()
MYSTERY_RECT = MYSTERY_IMAGE.get_rect()
MYSTERY_RECT.topleft = (650,80)
BULLET_WIDTH = 5
BULLET_HEIGHT = 15
BULLET_IMAGE = pygame.Surface((BULLET_WIDTH,BULLET_HEIGHT),flags=pygame.SRCALPHA)
BULLET_IMAGE.fill("lightyellow")
PLAYER_VEL = 3
BULLET_VEL = 5
alien_direction = 1
aliens = []
bullets = []
alien_bullets = []
joysticks = []
game_over = False
won = False
display_mystery = False
score = 0
lives = 3
ALIEN_LASER = pygame.USEREVENT + 1
pygame.time.set_timer(ALIEN_LASER,700)
MYSTERY_CLOCK = pygame.time.Clock()
MYSTERY_SPAWN_TIME = 5
MYSTERY_VEL = 3
mystery_timer = 0
LIFE_IMAGE = pygame.image.load("images/player.png").convert_alpha()
LIFE_X_START_POS = WINDOW_WIDTH - (LIFE_IMAGE.get_size()[0] * 2 + 20)

def reset_game():
    global lives, score
    pygame.mixer.music.unload()
    pygame.mixer.music.load("Music/grey sector.mp3")
    pygame.mixer.music.play(loops=-1)
    aliens.clear()
    PLAYER_RECT.center = (WINDOW_WIDTH/2,WINDOW_HEIGHT-18)
    score = 0
    bullets.clear()
    alien_bullets.clear()
    lives = 3
    spawn_aliens(6,8)

def display_lives():
    for live in range(lives - 1):
        x = LIFE_X_START_POS + (live * (LIFE_IMAGE.get_size()[0] + 10))
        WINDOW.blit(LIFE_IMAGE,(x,8))
        
def move_mystery():
    global mystery_timer, display_mystery
    if not won:
        mystery_timer += MYSTERY_CLOCK.tick() / 1000
        if mystery_timer >= MYSTERY_SPAWN_TIME:
            display_mystery = True
            MYSTERY_RECT.x -= MYSTERY_VEL
            if MYSTERY_RECT.x + MYSTERY_RECT.width < 0:
                MYSTERY_RECT.topleft = (650,80)
                mystery_timer = 0
                display_mystery = False
        
def check_collisions():
    global score, lives, game_over
    global display_mystery, mystery_timer
    for bullet_rect in bullets[:]:
        if bullet_rect.colliderect(MYSTERY_RECT):
            score += 100
            display_mystery = False
            mystery_timer = 0
            MYSTERY_RECT.topleft = (650,80)
            bullets.remove(bullet_rect)
    for alien_info in aliens[:]:
        alien_rect = alien_info[0]
        if alien_rect.bottom > WINDOW_HEIGHT or alien_rect.colliderect(PLAYER_RECT):
            game_over = True
        for bullet_rect in bullets[:]:
            if bullet_rect.colliderect(alien_rect):
                if alien_info[1] is RED_INVADER_IMAGE:
                    score += 20
                if alien_info[1] is GREEN_INVADER_IMAGE:
                    score += 55
                if alien_info[1] is YELLOW_INVADER_IMAGE:
                    score += 75
                EXPLOSION_SOUND.play()
                aliens.remove(alien_info)
                bullets.remove(bullet_rect)
    for alien_bullet_rect in alien_bullets[:]:
       if alien_bullet_rect.colliderect(PLAYER_RECT):
           alien_bullets.remove(alien_bullet_rect)
           if not won:
               lives -= 1
               if lives == 0:
                 pygame.mixer.music.stop()
                 pygame.mixer.music.unload()
                 pygame.mixer.music.load("music/game over.mp3")
                 pygame.mixer.music.play(loops=-1)
                 display_mystery = False
                 game_over = True
def fire():
        LASER_SOUND.play()
        bullet = pygame.Rect(PLAYER_RECT.x + (PLAYER_RECT.width // 2)-2,PLAYER_RECT.y-8,BULLET_WIDTH,BULLET_HEIGHT)
        bullets.append(bullet)

def alien_fire():
    if len(aliens) > 0:
        random_alien_rect = random.choice(aliens)[0]
        alien_center_x, alien_center_y = random_alien_rect.center
        LASER_SOUND.play()
        alien_bullet = pygame.Rect(alien_center_x,alien_center_y,BULLET_WIDTH,BULLET_HEIGHT)
        alien_bullets.append(alien_bullet)

def draw_text(x,y,size,text):
    font = pygame.font.Font("fonts/pixel.ttf",size)
    text_image = font.render(text,True,pygame.Color(255,255,255))
    text_rect = text_image.get_rect()
    text_rect.center = (x,y)
    WINDOW.blit(text_image,text_rect)
    
def spawn_aliens(rows,cols,x_distance=60,y_distance=48,x_offset=90,y_offset=125):
    for row_index, row in enumerate(range(rows)):
        for col_index, col in enumerate(range(cols)):
            x = col_index * x_distance + x_offset
            y = row_index * y_distance + y_offset
            ALIEN_WIDTH = 40
            ALIEN_HEIGHT = 32
            alien = pygame.Rect(x,y,ALIEN_WIDTH,ALIEN_HEIGHT)
            if row_index == 0:
                aliens.append((alien,YELLOW_INVADER_IMAGE))
            elif 1 <= row_index <= 2:
                aliens.append((alien,GREEN_INVADER_IMAGE))
            else:
                aliens.append((alien,RED_INVADER_IMAGE))

def move_aliens():
    for alien_info in aliens:
        alien_rect = alien_info[0]
        global alien_direction
        if alien_rect.right >= WINDOW_WIDTH:
            alien_direction = -1
            move_aliens_down()
        if alien_rect.left <= 0:
            alien_direction = 1
            move_aliens_down()
        alien_rect.x += alien_direction
            
def move_aliens_down():
    for alien_rect, _ in aliens:
        alien_rect.y += 2

def move_bullets():
    for bullet_rect in bullets[:]:
        bullet_rect.y -= BULLET_VEL
        if bullet_rect.bottom < 0:
            bullets.remove(bullet_rect)
    for bullet_rect in alien_bullets[:]:
        bullet_rect.y += BULLET_VEL
        if bullet_rect.top > WINDOW_HEIGHT:
            alien_bullets.remove(bullet_rect)
    
def move_player():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        PLAYER_RECT.x -= PLAYER_VEL
    elif keys[pygame.K_d]:
        PLAYER_RECT.x += PLAYER_VEL
    if PLAYER_RECT.left <= 30:
        PLAYER_RECT.left = 30
    if PLAYER_RECT.right >= WINDOW_WIDTH - 30:
        PLAYER_RECT.right = WINDOW_WIDTH - 30

def move_player_controller():
    for joystick in joysticks:
        horizontal = joystick.get_axis(0)
        if horizontal < -0.4:
            PLAYER_RECT.x -= PLAYER_VEL
        elif horizontal > 0.4:
            PLAYER_RECT.x += PLAYER_VEL
        
def update():
    if not game_over:
        move_mystery()
        move_player()
        move_player_controller()
        move_aliens()
        move_bullets()
        check_collisions()

def draw():
    global won, display_mystery
    WINDOW.fill(BACKGROUND_COLOUR)
    if display_mystery:
        WINDOW.blit(MYSTERY_IMAGE,MYSTERY_RECT)
    WINDOW.blit(PLAYER_IMAGE,PLAYER_RECT)
    if not game_over:
        for alien_info in aliens:
            alien_rect = alien_info[0]
            alien_image = alien_info[1]
            WINDOW.blit(alien_image,alien_rect)
        for bullet_rect in bullets:
            WINDOW.blit(BULLET_IMAGE,bullet_rect)
        for bullet_rect in alien_bullets:
            WINDOW.blit(BULLET_IMAGE,bullet_rect)
        if len(aliens) <=0:
            draw_text(WINDOW_WIDTH // 2,WINDOW_HEIGHT // 2,32,"You won")
            display_mystery = False
            won = True
        draw_text(322,30,20,"Score:"+str(score))
    elif game_over:
        draw_text(WINDOW_WIDTH // 2,WINDOW_HEIGHT // 2,32,"You lost")
    display_lives()
    
def game():
    running = True
    spawn_aliens(6,8)
    while running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.unload()
                running = False
            if event.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(event.device_index)
                joysticks.append(joystick)
            global game_over, won
            if not game_over and not won:
                if event.type == ALIEN_LASER:
                    alien_fire()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    fire()
                if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    fire()
            elif won and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()
                won = False
            elif won and event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                reset_game()
                won = False
            elif game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()
                game_over = False
            elif game_over and event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                reset_game()
                game_over = False
        update()
        draw()
        
        pygame.display.flip()
    pygame.quit()
    
if __name__ == "__main__":    
    game()
