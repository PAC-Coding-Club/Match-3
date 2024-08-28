import pygame
import random
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

class Board:
    def __init__(self, location=(100, 100)):
        self.tiles = []
        for i in range(8):
            for j in range(8):
                # Randomly choose between red, green, or blue
                color_choice = random.choice(['red', 'orange', 'yellow', 'green', 'blue', 'purple'])

                if color_choice == 'red':
                    color = (255, 0, 0)  # Red color
                elif color_choice == 'orange':
                    color = (255, 165, 0)  # Orange color
                elif color_choice == 'yellow':
                    color = (255, 255, 0)  # Yellow color
                elif color_choice == 'green':
                    color = (0, 255, 0)  # Green color
                elif color_choice == 'blue':
                    color = (0, 0, 255)  # Blue color
                elif color_choice == 'purple':
                    color = (128, 0, 128)  # Purple color

                tile = Tile(color, (30, 30), (i * 30 + location[0], j * 30 + location[1]))
                self.tiles.append(tile)

        self.selected = None

    def draw(self, screen):
        for tile in self.tiles:
            screen.blit(tile.image, tile.rect)

    def update(self):
        # Check for match-3s
        tile_color_dict = {}
        for tile in self.tiles:
            tile_color_dict[tile.unmoved_center] = tile.color
        matches = match_3(tile_color_dict)
        for match in matches:
            for coord in match["coordinates"]:
                for i, tile in enumerate(self.tiles):
                    if tile.rect.center == coord:
                        self.tiles.remove(tile)

        # Move the tile if one is selected
        if self.selected:
            tile = self.selected
            mouse = pygame.Vector2(pygame.mouse.get_pos())
            difference = mouse - pygame.Vector2(tile.unmoved_center)

            if abs(difference.x) > abs(difference.y):
                clamped_x = max(tile.unmoved_center[0] - 29, min(tile.unmoved_center[0] + 29, mouse.x))
                tile.rect.centerx = clamped_x
                tile.rect.centery = tile.unmoved_center[1]
            else:
                clamped_y = max(tile.unmoved_center[1] - 29, min(tile.unmoved_center[1] + 29, mouse.y))
                tile.rect.centery = clamped_y
                tile.rect.centerx = tile.unmoved_center[0]

        # Fill gaps
        for tile in self.tiles:
            tile.rect.move_ip(0, 30)

            other_tiles = self.tiles.copy()
            other_tiles.remove(tile)
            if tile.rect.collideobjects(other_tiles) or tile.rect.y > 400:
                tile.rect.move_ip(0, -30)
            else:
                tile.unmoved_center = tile.rect.center

class Tile(pygame.sprite.Sprite):
    def __init__(self, color, size, location):
        super().__init__()
        self.color = color
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = location

        self.unmoved_center = self.rect.center


def match_3(tile_color_dict):
    consecutive_colors_info = []

    # Convert keys to sorted lists of x and y values
    x_coords = sorted(set(key[0] for key in tile_color_dict))
    y_coords = sorted(set(key[1] for key in tile_color_dict))

    # Check rows for consecutive colors
    for y in y_coords:
        for i in range(len(x_coords) - 2):
            color1 = tile_color_dict.get((x_coords[i], y))
            color2 = tile_color_dict.get((x_coords[i + 1], y))
            color3 = tile_color_dict.get((x_coords[i + 2], y))
            if color1 == color2 == color3:
                consecutive_colors_info.append({
                    'color': color1,
                    'coordinates': [(x_coords[i], y), (x_coords[i + 1], y), (x_coords[i + 2], y)]
                })

    # Check columns for consecutive colors
    for x in x_coords:
        for j in range(len(y_coords) - 2):
            color1 = tile_color_dict.get((x, y_coords[j]))
            color2 = tile_color_dict.get((x, y_coords[j + 1]))
            color3 = tile_color_dict.get((x, y_coords[j + 2]))
            if color1 == color2 == color3:
                consecutive_colors_info.append({
                    'color': color1,
                    'coordinates': [(x, y_coords[j]), (x, y_coords[j + 1]), (x, y_coords[j + 2])]
                })

    return consecutive_colors_info


board = Board()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for tile in board.tiles:
                if tile.rect.collidepoint(event.pos):
                    board.selected = tile
        if event.type == pygame.MOUSEBUTTONUP:
            tile = board.selected
            if tile:
                # find colliding tiles
                collides = tile.rect.collideobjectsall(board.tiles)
                collide_tiles = []
                for sub_tile in collides:
                    if sub_tile != tile:
                        collide_tiles.append(sub_tile)
                if collide_tiles:
                    collided_tile = collide_tiles[0]

                    # Swap the tiles
                    tile.unmoved_center, collided_tile.unmoved_center = collided_tile.unmoved_center, tile.unmoved_center
                    tile.rect.center = tile.unmoved_center
                    collided_tile.rect.center = collided_tile.unmoved_center

            tile.rect.center = tile.unmoved_center
            # Deselect our tile
            board.selected = None

    board.update()
    board.draw(screen)

    pygame.display.update()
    screen.fill((60, 60, 60))
    clock.tick(60)
