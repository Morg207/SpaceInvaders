import pygame
import random
import sys

pygame.init()
pygame.joystick.init()
pygame.mixer.set_num_channels(16)

window_width = 650
window_height = 650
window = pygame.display.set_mode((window_width,window_height))
pygame.mouse.set_visible(False)
pygame.mixer.music.load("music/grey sector.mp3")
pygame.mixer.music.play(loops=-1)
pygame.display.set_caption("Space Invaders")
window_icon = pygame.image.load("images/window icon.png").convert_alpha()
window_icon = pygame.transform.scale(window_icon,(32,32))
pygame.display.set_icon(window_icon)
background_colour = (70,70,70)
clock = pygame.time.Clock()
fps = 60
player_image = pygame.image.load("images/player.png").convert_alpha()
player_rect = player_image.get_rect()
player_rect.center = (window_width/2,window_height-18)
laser_sound = pygame.mixer.Sound("sounds/laser.ogg")
explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
red_invader_image = pygame.image.load("images/red invader.png").convert_alpha()
green_invader_image = pygame.image.load("images/green invader.png").convert_alpha()
yellow_invader_image = pygame.image.load("images/yellow invader.png").convert_alpha()
mystery_image = pygame.image.load("images/mystery ship.png").convert_alpha()
mystery_rect = mystery_image.get_rect()
mystery_rect.topleft = (650,80)
bullet_width = 5
bullet_height = 14
bullet_image = pygame.Surface((bullet_width,bullet_height),flags=pygame.SRCALPHA)
bullet_image.fill("lightyellow")
player_vel = 3
bullet_vel = 5
game_state = {"score": 0, "lives":3,"mystery_timer":0,
              "game_over":False,"won":False,"display_mystery":False,"alien_direction": 1}
aliens = []
bullets = []
alien_bullets = []
alien_laser = pygame.USEREVENT + 1
pygame.time.set_timer(alien_laser,700)
mystery_spawn_time = 5
mystery_vel = 3
life_image = pygame.image.load("images/player.png").convert_alpha()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

def draw_text(x,y,size,text):
    font = pygame.font.Font("fonts/pixel.ttf",size)
    text_image = font.render(text,True,pygame.Color(255,255,255))
    text_rect = text_image.get_rect()
    text_rect.center = (x,y)
    window.blit(text_image,text_rect)

def reset_game():
    pygame.mixer.music.unload()
    pygame.mixer.music.load("Music/grey sector.mp3")
    pygame.mixer.music.play(loops=-1)
    aliens.clear()
    player_rect.center = (window_width/2,window_height-18)
    game_state["score"] = 0
    game_state["lives"] = 3
    game_state["mystery_timer"] = pygame.time.get_ticks()/1000
    bullets.clear()
    alien_bullets.clear()
    spawn_aliens(6,8)
    mystery_rect.topleft = (650,80)

def display_lives():
    life_image_width = life_image.get_size()[0]
    life_x_start_pos = window_width - (life_image_width * 2 + 20)
    for life in range(game_state["lives"]- 1):
        x = life_x_start_pos + (life * (life_image_width + 10))
        window.blit(life_image,(x,8))
        
def move_mystery():
    if not game_state["won"]:
        if pygame.time.get_ticks()/1000 - game_state["mystery_timer"] > mystery_spawn_time:
            game_state["display_mystery"] = True
            mystery_rect.x -= mystery_vel
            if mystery_rect.x + mystery_rect.width < 0:
                mystery_rect.topleft = (650,80)
                game_state["mystery_timer"] = pygame.time.get_ticks()/1000
                game_state["display_mystery"] = False

def collide_with_mystery():
    for bullet_rect in bullets[:]:
        if bullet_rect.colliderect(mystery_rect):
            game_state["score"]+= 100
            game_state["display_mystery"] = False
            game_state["mystery_timer"] = pygame.time.get_ticks()/1000
            mystery_rect.topleft = (650,80)
            bullets.remove(bullet_rect)
            explosion_sound.play()

def collide_with_aliens():
    for alien_info in aliens[:]:
        alien_rect = alien_info[0]
        alien_image = alien_info[1]
        if alien_rect.bottom > window_height or alien_rect.colliderect(player_rect):
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load("music/game over.mp3")
            pygame.mixer.music.play(loops=-1)
            game_state["game_over"] = True
            game_state["display_mystery"] = False
        for bullet_rect in bullets[:]:
            if bullet_rect.colliderect(alien_rect):
                if alien_info[1] is red_invader_image:
                    game_state["score"] += 20
                if alien_info[1] is green_invader_image:
                    game_state["score"] += 55
                if alien_info[1] is yellow_invader_image:
                    game_state["score"] += 75
                explosion_sound.play()
                bullets.remove(bullet_rect)
                aliens.remove(alien_info)

def collide_with_player():
    for alien_bullet_rect in alien_bullets[:]:
       if alien_bullet_rect.colliderect(player_rect) and not game_state["won"]:
           alien_bullets.remove(alien_bullet_rect)
           game_state["lives"] -= 1
           if game_state["lives"] == 0:
              pygame.mixer.music.stop()
              pygame.mixer.music.unload()
              pygame.mixer.music.load("music/game over.mp3")
              pygame.mixer.music.play(loops=-1)
              game_state["display_mystery"] = False
              game_state["game_over"] = True
    
def fire():
        laser_sound.play()
        bullet = pygame.Rect(player_rect.x + (player_rect.width // 2)-2,player_rect.y-8,bullet_width,bullet_height)
        bullets.append(bullet)

def alien_fire():
    if len(aliens) > 0:
        random_alien_rect = random.choice(aliens)[0]
        alien_center_x, alien_center_y = random_alien_rect.center
        laser_sound.play()
        alien_bullet = pygame.Rect(alien_center_x,alien_center_y,bullet_width,bullet_height)
        alien_bullets.append(alien_bullet)
    
def spawn_aliens(rows,cols,x_distance=60,y_distance=48,x_offset=90,y_offset=125):
    for row_index, row in enumerate(range(rows)):
        for col_index, col in enumerate(range(cols)):
            x = col_index * x_distance + x_offset
            y = row_index * y_distance + y_offset
            alien_width = 40
            alien_height = 32
            alien = pygame.Rect(x,y,alien_width,alien_height)
            if row_index == 0:
                aliens.append((alien,yellow_invader_image))
            elif 1 <= row_index <= 2:
                aliens.append((alien,green_invader_image))
            else:
                aliens.append((alien,red_invader_image))

def move_aliens():
    for alien_info in aliens:
        alien_rect = alien_info[0]
        if alien_rect.right >= window_width:
            game_state["alien_direction"] = -1
            for alien, _ in aliens:
                alien.y += 2
        if alien_rect.left <= 0:
            game_state["alien_direction"] = 1
            for alien, _ in aliens:
                alien.y += 2
        alien_rect.x += game_state["alien_direction"]
            
def move_bullets():
    for bullet_rect in bullets[:]:
        bullet_rect.y -= bullet_vel
        if bullet_rect.bottom < 0:
            bullets.remove(bullet_rect)
    for bullet_rect in alien_bullets[:]:
        bullet_rect.y += bullet_vel
        if bullet_rect.top > window_height:
            alien_bullets.remove(bullet_rect)
    
def move_player():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_rect.x -= player_vel
    elif keys[pygame.K_d]:
        player_rect.x += player_vel
    if player_rect.left <= 30:
        player_rect.left = 30
    if player_rect.right >= window_width - 30:
        player_rect.right = window_width - 30

def move_player_controller():
    for joystick in joysticks:
        horizontal = joystick.get_axis(0)
        if horizontal < -0.4:
            player_rect.x -= player_vel
        elif horizontal > 0.4:
            player_rect.x += player_vel
        
def update():
    if not game_state["game_over"]:
        move_mystery()
        move_player()
        move_player_controller()
        move_aliens()
        move_bullets()
        collide_with_mystery()
        collide_with_aliens()
        collide_with_player()

def draw():
    window.fill(background_colour)
    if game_state["display_mystery"]:
        window.blit(mystery_image,mystery_rect)
    if not game_state["game_over"]:
        display_lives()
        if not game_state["won"]:
            window.blit(player_image,player_rect)
            for alien_rect, alien_image in aliens:
                window.blit(alien_image,alien_rect)
            for bullet_rect in bullets:
                window.blit(bullet_image,bullet_rect)
            for bullet_rect in alien_bullets:
                window.blit(bullet_image,bullet_rect)
        if len(aliens) <=0:
            draw_text(window_width // 2,window_height // 2,32,"You won")
            game_state["display_mystery"] = False
            game_state["won"] = True
        draw_text(322,30,20,"Score:"+str(game_state["score"]))
    else:
        draw_text(window_width // 2,window_height // 2,32,"You lost")

if __name__ == "__main__":
    running = True
    spawn_aliens(6,8)
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.JOYDEVICEADDED:
                joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if event.type == pygame.JOYDEVICEREMOVED:
                joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if not game_state["game_over"] and not game_state["won"]:
                if event.type == alien_laser:
                    alien_fire()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    fire()
                if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    fire()
            elif game_state["won"] and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    reset_game()
                    game_state["won"] = False
            elif game_state["won"] and event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    reset_game()
                    game_state["won"] = False
            elif game_state["game_over"] and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    reset_game()
                    game_state["game_over"] = False
            elif game_state["game_over"] and event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    reset_game()
                    game_state["game_over"] = False
        update()
        draw()
        pygame.display.flip()
    pygame.mixer.music.unload()
    pygame.quit()
    sys.exit()
