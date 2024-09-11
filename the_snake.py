import time
from collections import deque
from random import choice

import pygame

# Field and grid sizes
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
ALL_CELLS = {
    (pos_x, pos_y)
    for pos_x in range(0, SCREEN_WIDTH, GRID_SIZE)
    for pos_y in range(0, SCREEN_HEIGHT, GRID_SIZE)
}

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (0, 255, 0)
POISON_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 0, 255)

# Snake speed
SPEED = 10

# Time for change poison position (sec)
CHANGE_POISON = 5

# Poison offset (cells)
OFFSET_POISON = 5

# Setting up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Game field window title
pygame.display.set_caption('Змейка')

# Time setting
clock = pygame.time.Clock()


class GameObject:
    """Base class for game objects."""

    def __init__(self) -> None:
        self.position = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.body_color = None

    @staticmethod
    def draw_cell(position: tuple, body_color: tuple):
        """
        Draw the cell on the screen.
        :param position: position of the cell.
        :param body_color: color of the cell.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, body_color, rect)
        if body_color != BOARD_BACKGROUND_COLOR:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Draw the object on the screen."""
        raise NotImplementedError


class Item(GameObject):
    """Class representing item for snake on the game board."""

    def __init__(self, used_cells: list[tuple] | tuple[tuple] = ()) -> None:
        super().__init__()
        self.position = None
        self.last = None
        self.randomize_position(used_cells)

    def randomize_position(
            self,
            used_cells: list[tuple] | tuple[tuple] = ()
    ) -> tuple[int, int]:
        """
        Randomly generate a position for the item on the game board.
        :param used_cells: used cells.
        :return: tuple of random x and y coordinates.
        """
        self.last = self.position
        self.position = choice(tuple(ALL_CELLS - set(used_cells)))

    def draw(self):
        """Draw the object on the screen."""
        self.draw_cell(self.position, self.body_color)
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
            self.last = None


class Apple(Item):
    """Class representing an apple on the game board."""

    def __init__(self, used_cells: list[tuple] | tuple[tuple] = ()) -> None:
        super().__init__(used_cells)
        self.body_color = APPLE_COLOR


class Poison(Item):
    """Class representing a poison on the game board."""

    def __init__(
            self,
            used_cells: list[tuple] | tuple[tuple] = ()
    ) -> None:
        super().__init__(used_cells)
        self.body_color = POISON_COLOR

    def new_position_for_direction(
            self,
            head_position: tuple,
            direction: tuple
    ) -> None:
        """
        Generate new position from position of the snake.
        :param head_position: position of the snake's head.
        :param direction: direction of the snake.
        """
        self.last = self.position
        offset_poison = [pos * GRID_SIZE * 5
                         for pos in direction]
        new_pos_x = (head_position[0] + offset_poison[0]) % SCREEN_WIDTH
        new_pos_y = (head_position[1] + offset_poison[1]) % SCREEN_HEIGHT
        self.position = (new_pos_x, new_pos_y)


class Snake(GameObject):
    """Class representing the snake on the game board."""

    def __init__(self) -> None:
        super().__init__()
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.body_color = SNAKE_COLOR
        # Used deque, because add value with complexity O(1).
        self.positions = [self.position]
        self.last = None

    def update_direction(self):
        """Update the snake's direction."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Move the snake forward in its current direction."""
        current_x_pos, current_y_pos = self.get_head_position()
        next_x_pos = (
            (current_x_pos + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        )
        next_y_pos = (
            (current_y_pos + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )
        if (next_x_pos, next_y_pos) in self.positions:
            self.reset()
        else:
            self.positions.insert(
                0,
                (next_x_pos, next_y_pos)
            )
            self.last = self.positions.pop()

    def draw(self):
        """Draw the object on the screen."""
        self.draw_cell(self.positions[0], self.body_color)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """
        Get the position of the snake's head.
        :return: tuple of x and y coordinates of the snake's head.
        """
        return self.positions[0]

    def reset(self):
        """Reset the snake to its initial position."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
        self.positions = deque(((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),))

    def increase(self):
        """Increase the snake's length by one."""
        self.positions.insert(0, self.get_head_position())

    def decrease(self):
        """Decrease the snake's length by one."""
        if len(self.positions) > 1:
            rect = pygame.Rect(self.positions.pop(), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


def handle_keys(game_object: Snake):
    """
    Handle keyboard input to control the game object.
    :param game_object: Game object to control.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Main function for the game.
    Starts the game loop and handles key inputs.
    """
    pygame.init()

    snake = Snake()
    apple = Apple(snake.positions)
    poison = Poison((*snake.positions, apple.position))

    update_poison = time.time() + 3

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.increase()
            apple.randomize_position(snake.positions)

        if snake.get_head_position() == poison.position:
            snake.decrease()
            poison.randomize_position((*snake.positions, apple.position))
        elif (time_now := time.time()) > update_poison:
            poison.new_position_for_direction(
                snake.get_head_position(), snake.direction
            )
            update_poison = time_now + CHANGE_POISON

        apple.draw()
        poison.draw()
        snake.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
