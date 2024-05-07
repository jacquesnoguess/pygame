import pygame
import random

pygame.font.init()
my_font = pygame.font.SysFont('Elephant', 30)
pygame.mixer.init()
pygame.init()

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
score = 0

class Score(pygame.sprite.Sprite):
    def __init__(self):
        super(Score, self).__init__()

    def display_score(self, screen):
        text_surface = my_font.render('SCORE: '+str(score), False, (0, 0, 0))
        screen.blit(text_surface, (0, 0))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("jet.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bullet, self).__init__()
        self.surf = pygame.Surface((15, 3))
        self.surf.fill((255, 255, 237))
        self.rect = self.surf.get_rect(center=(x, y))
        self.speed = 10  # Adjust the bullet speed as needed

    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite): 
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 15)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()
            
class Explosion(pygame.sprite.Sprite):
    def __init__(self, explosion_x, explosion_y):
        super(Explosion, self).__init__()
        self.image = pygame.image.load("explosion.png").convert()
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.image.get_rect(center=(explosion_x, explosion_y))
        self.duration = 500  # Duration in milliseconds
        self.start_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.kill()


# Load sounds
pygame.mixer.music.load("minor synth.wav")
pygame.mixer.music.play(loops=-1)
move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
collision_sound = pygame.mixer.Sound("Collision.ogg")
victory_sound = pygame.mixer.Sound("victory.wav")

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set up events
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 1000)

# Create sprite groups
player = Player()
enemies = pygame.sprite.Group()
clouds = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Set up the clock
clock = pygame.time.Clock()

# Main loop
running = True
score = 0
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_SPACE:
                # Create a new bullet instance and add it to the bullet group
                new_bullet = Bullet(player.rect.right, player.rect.centery)
                all_sprites.add(new_bullet)
        elif event.type == QUIT:
            running = False
        elif event.type == ADDENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
        elif event.type == ADDCLOUD:
            new_cloud = Cloud()
            clouds.add(new_cloud)
            all_sprites.add(new_cloud)

    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    # Update bullet position
    for bullet in all_sprites:
        if isinstance(bullet, Bullet):
            bullet.update()

    # Update enemy position
    enemies.update()
    # Update cloud position
    clouds.update()

    screen.fill((135, 206, 250))

    # Blit all sprites
    for entity in all_sprites:
        if isinstance(entity, Explosion):
            screen.blit(entity.image, entity.rect)
        else:
            screen.blit(entity.surf, entity.rect)

    # Check for collisions
    if pygame.sprite.spritecollideany(player, enemies):
        victory_sound.play
        player.kill()
        running = False
    
    for bullet in all_sprites:
        if isinstance(bullet, Bullet):
            enemies_hit = pygame.sprite.spritecollide(bullet, enemies, True)
            if enemies_hit:
                collision_sound.play()
                # Iterate over the enemies that were hit
                for enemy_hit in enemies_hit:
                    # Get the coordinates of the enemy missile
                    explosion_x = enemy_hit.rect.centerx
                    explosion_y = enemy_hit.rect.centery
                    # Spawn explosion at the enemy missile's coordinates
                    explosion = Explosion(explosion_x, explosion_y)
                    all_sprites.add(explosion)
                    score += 1
                bullet.kill()

    # Display score
    score_display = Score()
    score_display.display_score(screen)
    
    # Update explosions
    for explosion in all_sprites:
        if isinstance(explosion, Explosion):
            explosion.update()
    
    pygame.display.flip()

    clock.tick(60)

pygame.mixer.music.stop()
pygame.mixer.quit()

