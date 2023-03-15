import pygame
import sys
from level import Level
import asyncio


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((32 * 20, 32 * 16))
        self.clock = pygame.time.Clock()

        self.level = Level()
        pygame.display.set_caption('THIS IS NOT A RAGE GAME')
        pygame.mouse.set_visible(False)

    async def run(self):
        while True:
            self.screen.fill((252, 223, 205))
            # print(pygame.mouse.get_pos())
            # self.screen.fill('white')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
            self.level.run()
            self.clock.tick(60)
            pygame.display.update()
            await asyncio.sleep(0)


if __name__ == '__main__':
    game = Game()
    asyncio.run(game.run())
