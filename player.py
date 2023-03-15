import pygame

from support import import_animations


class Player(pygame.sprite.Sprite):
    def __init__(self, *groups, pos=(0, 250), obstacle_sprites=pygame.sprite.Group()):
        super().__init__(*groups)
        self.sprite_type = 'entity'
        self.image = pygame.transform.scale(pygame.image.load('graphics/player/0.png'), (32, 32))
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2()
        self.obstacle_sprites = obstacle_sprites
        self.groups = groups
        self.gravity_speed = 0.8
        self.speed = 4
        self.on_ground = False
        self.on_ceiling = False
        self.status = 'idle'
        self.flip = False
        self.frame = 0
        self.animation_speed = 0.075
        self.animations = import_animations('graphics/player')
        self.shooting = False
        self.ammo = [Bullet(*groups, player=self)]
        self.health = 1000
        self.full_health = 1000
        self.interact = False

    def apply_gravity(self):
        self.direction.y += self.gravity_speed
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = -16

    def animate(self):
        if self.status == 'run':
            self.frame += self.animation_speed
            if self.frame > len(self.animations) - 1:
                self.frame = 0

            surface = self.animations[str(int(self.frame))]
            image = pygame.transform.scale(surface, (surface.get_width() * 2, surface.get_height() * 2))
        elif self.status == 'shoot':
            surface = self.animations['shoot']
            image = pygame.transform.scale(surface, (surface.get_width() * 2, surface.get_height() * 2))
        else:
            surface = self.animations['0']
            image = pygame.transform.scale(surface, (surface.get_width() * 2, surface.get_height() * 2))
        self.image = pygame.transform.flip(image, self.flip, False)

    def get_status(self):
        if self.direction.x > 0:
            self.flip = False
        elif self.direction.x < 0:
            self.flip = True
        if abs(self.direction.x) > 0:
            # print(True)
            self.status = 'run'
        else:
            if self.shooting:
                self.status = 'shoot'
            else:
                self.status = 'idle'
        if self.health <= 0:
            self.kill()

    def get_key_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.on_ground:
            self.jump()

        if keys[pygame.K_SPACE]:
            self.shooting = True
            self.interact = True
            self.fire()
        else:
            self.shooting = False
            self.interact = False

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def fire(self):
        self.ammo.append(Bullet(self.groups, player=self))

    def move_bullet(self):
        for bullet in self.ammo:
            bullet.move()

    def update(self):
        self.move_bullet()
        self.get_status()
        self.animate()
        self.get_key_input()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, *groups, player=None):
        super().__init__(*groups)
        self.image = pygame.transform.flip(pygame.image.load('graphics/tiles/23.png').convert_alpha(), player.flip, False)

        self.player = player
        self.x = self.fire()
        self.life_span = 100

    def fire(self):
        self.flip = self.player.flip
        if self.flip:
            x = -1
            self.rect = self.image.get_rect(topright=self.player.rect.midleft)
        else:
            x = 1
            self.rect = self.image.get_rect(topleft=self.player.rect.midright)
        return x

    def move(self):
        self.rect.x += self.x * 20
        if self.life_span > 0:
            self.life_span -= 1
        else:
            self.kill()
