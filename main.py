import pygame

import yaml
from typing import Any

'''
Used https://www.geeksforgeeks.org/python/python-yaml-module/ as a reference for using a YAML to initialize game.
'''
# config file path
config = 'config.yml'

with open(config) as f:
    yaml_data: dict[str, Any] = yaml.load(
        f, Loader=yaml.FullLoader)  # data from config file


class Game(object):
    def __init__(self, args: dict[Any, Any] = {}) -> None:
        pygame.init()
        if not args:
            self.screen: pygame.Surface = pygame.display.set_mode((800, 600))
            self.clock = pygame.time.Clock()

    def update(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        self.screen.fill("purple")

        pygame.display.flip()

        self.clock.tick(60)


print(yaml_data)
game: Game = Game()
pygame.quit()
