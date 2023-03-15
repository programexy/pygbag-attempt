import os.path
import sys

import pygame
from npc import NonPlayableCharacter
from enemy import Enemy
from player import Player
from support import import_csv_layout
from tile import Tile


class Level:
    def __init__(self):
        self.visible_sprites = YSortCameraGROUP()
        self.obstacle_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.finish_sprite = pygame.sprite.GroupSingle()
        self.display_surface = pygame.display.get_surface()
        self.player_spawn_point = (None, None)
        self.level = 1
        self.player = None
        self.npc_message = 'DO NOT TRUST THE PLATFORMS!'

        self.set_up_map()

    def get_npc_message(self):
        if self.level == 3:
            self.npc_message = 'Do not trust the platforms!'
        if self.level == 4:
            self.npc_message = 'Worm land? Yep, this is what it is. No finish? That is a lie.'
        if self.level == 5:
            self.npc_message = 'THis is very buggy right? Hope you do not bee mad! :P'
        if self.level == 6:
            self.npc_message = 'WWWOOOOOAAAHHHH SOOOOOOOO LAAGGGYYYYYYY'
        if self.level == 7:
            self.npc_message = 'Almost everything invisible! Try your best though.'

    def check_finish(self):
        finish_sprite = self.finish_sprite.sprite
        if self.player.rect.colliderect(finish_sprite.rect):
            if os.path.exists(f'Tilemap/level{self.level + 1}'):
                self.level += 1
                self.visible_sprites = YSortCameraGROUP()
                self.obstacle_sprites = pygame.sprite.Group()
                self.enemy_sprites = pygame.sprite.Group()
                self.finish_sprite = pygame.sprite.GroupSingle()
                self.set_up_map()
            else:
                print('YOU WIN')
                pygame.quit()
                sys.exit()

    def enemy_attack(self):
        if pygame.sprite.spritecollideany(self.player, self.enemy_sprites):
            self.player.health -= 1

    def set_up_map(self):
        self.get_npc_message()
        layouts = import_csv_layout(f'Tilemap/level{self.level}')
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    x = col_index * 32
                    y = row_index * 32
                    if style == 'entities':
                        if col == '40':
                            self.player = Player(self.visible_sprites, pos=(x, y))
                            self.player_spawn_point = (x,y)
                        elif col == '51':
                            Enemy(self.visible_sprites, self.enemy_sprites, pos=(x, y))
                        elif col == '53':
                            Enemy(self.visible_sprites, self.enemy_sprites, pos=(x, y), mob='fly')
                        elif col == '55':
                            Enemy(self.visible_sprites, self.enemy_sprites, pos=(x, y), mob='worm', gravity=0.8)
                        elif col == '45':
                            if self.player:
                                NonPlayableCharacter(self.visible_sprites, pos=(x,y), player=self.player, message=self.npc_message)
                    if style == 'obstacle':
                        if col == '43':
                            if self.level == 7:
                                print(True)
                                img = pygame.Surface((32,32))
                                img.set_alpha(100)
                                Tile(self.obstacle_sprites, self.visible_sprites, pos=(x, y), image=img)
                            else:
                                Tile(self.obstacle_sprites, pos=(x, y))
                    if style == 'finish':
                        if col == '50':
                            self.finish_sprite.add(Tile(pos=(x, y)))

    def horizontal_movement_collision(self, sprite):
        player = sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.obstacle_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True

                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True

    def vertical_movement_collision(self, sprite):
        player = sprite
        player.apply_gravity()
        collidable_sprites = self.obstacle_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def shoot_enemy_check(self):
        for bullet in self.player.ammo:
            for sprite in self.enemy_sprites.sprites():
                if sprite.rect.colliderect(bullet.rect):
                    bullet.kill()
                    sprite.health -= 1
                    sprite.rect.x += self.player.direction.x * -1
                    sprite.rect.y -= 5

    def check_fall(self):
        if self.player.rect.y > 1024+32*20:
            self.player.direction.y = 0
            self.player.rect.topleft = self.player_spawn_point

    def collisions(self):
        for sprite in [sprite for sprite in self.visible_sprites if
                       hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'entity']:
            self.horizontal_movement_collision(sprite)
            self.vertical_movement_collision(sprite)

    def run(self):
        self.visible_sprites.custom_draw(self.player, self.level)
        self.visible_sprites.enemy_ai(self.player)
        self.visible_sprites.update()
        self.collisions()
        self.shoot_enemy_check()
        self.check_finish()
        self.check_fall()
        self.enemy_attack()
        self.draw_player_health()

    def draw_player_health(self):
        margin = 2
        thickness = 5
        background_surf = pygame.Surface((int(self.player.full_health / 10) + margin*2, thickness + margin*2))
        self.display_surface.blit(background_surf, (5, 5))
        if self.player.health > 0:
            health_surf = pygame.Surface((int(self.player.health / 10), thickness))
            health_surf.fill('red')
            self.display_surface.blit(health_surf, (5+margin, 5+margin))
        else:
            pass


class YSortCameraGROUP(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player, level):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        background_image = pygame.transform.scale(pygame.image.load(f'graphics/map{level}.png').convert_alpha(),
                                                  (2048, 1024))
        background_rect = background_image.get_rect(topleft=(0, 0))
        self.display_surface.blit(background_image, background_rect.topleft - self.offset)

        for sprite in sorted(self.sprites(), key=lambda entity: entity.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_ai(self, player):
        for sprite in self.sprites():
            if hasattr(sprite, 'mob'):
                sprite.ai(player)
