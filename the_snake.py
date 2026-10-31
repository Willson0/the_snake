"""Игра «Змейка». Змейка ползает по полю и ест яблоки."""
from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
# Размер одной ячейки в пикселях (ширина и высота):
CELL_SIZE = (GRID_SIZE, GRID_SIZE)

# Центральная точка игрового поля:
CENTER_POSITION = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Все ячейки игрового поля:
ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Какое направление получит змейка, если нажать клавишу:
KEY_TO_DIRECTION = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Общий класс для всех объектов на поле.

    Здесь хранится то, что есть у каждого объекта: место на поле
    и цвет. Как объект выглядит, решает дочерний класс.

    Attributes:
        position: координаты верхнего левого угла объекта.
        body_color: цвет объекта в формате RGB.
    """

    def __init__(self):
        """Ставит объект в центр поля. Цвет пока не задан."""
        self.position = CENTER_POSITION
        self.body_color = None

    def draw(self):
        """Рисует объект на поле.

        В этом классе ничего не рисуем, это делают дочерние классы.
        """
        pass

    def draw_cell(self, position, color):
        """Закрашивает одну клетку поля.

        Клетка заливается цветом и обводится тонкой рамкой.

        Args:
            position: координаты верхнего левого угла клетки.
            color: цвет, которым залить клетку (RGB).
        """
        rect = pygame.Rect(position, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко. Занимает одну клетку и появляется в случайном месте."""

    def __init__(self, occupied_positions=()):
        """Создает яблоко и ставит его в свободное место.

        Args:
            occupied_positions: клетки, которые уже заняты змейкой.
                На них яблоко не появится. По умолчанию пусто.
        """
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбирает для яблока случайную свободную клетку.

        Берем все клетки поля и убираем из них занятые. Из оставшихся
        выбираем одну случайно.

        Args:
            occupied_positions: клетки, которые нельзя занимать.
                По умолчанию пусто.
        """
        free_cells = ALL_CELLS - set(occupied_positions)
        self.position = choice(tuple(free_cells))

    def draw(self):
        """Рисует яблоко на поле."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка. Хранит список своих кусочков и умеет ползти.

    Первый кусочек в списке — голова, последний — хвост.

    Attributes:
        positions: список координат всех кусочков, от головы к хвосту.
        length: сколько кусочков сейчас у змейки.
        direction: куда змейка ползет сейчас.
        next_direction: куда повернуть на следующем шаге, если
            нажали клавишу. Если не нажали, здесь None.
        last: координаты хвоста, который ушел на этом шаге.
            Нужны, чтобы стереть его с поля. Если хвост не ушел,
            здесь None.
    """

    def __init__(self):
        """Создает змейку из одной головы, которая ползет вправо."""
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.next_direction = None
        self.reset()
        # Сразу после запуска змейка ползет вправо:
        self.direction = RIGHT

    def reset(self):
        """Начинает игру заново.

        Змейка снова становится одной головой в центре поля.
        Направление выбирается случайно.
        """
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = choice(DIRECTIONS)
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Поворачивает змейку, если нажали клавишу.

        Если в next_direction что-то есть, переносим это в direction
        и очищаем next_direction. Если нет, ничего не делаем.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает координаты головы.

        Returns:
            Координаты первого кусочка в списке positions.
        """
        return self.positions[0]

    def move(self):
        """Двигает змейку на одну клетку.

        Добавляем новую голову в начало списка. Если голова уходит
        за край, она появляется с другой стороны поля. Если змейка
        не выросла, удаляем хвост и запоминаем его в last.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Рисует змейку.

        Сначала стираем хвост, который ушел на этом шаге. Потом
        рисуем голову. Остальные кусочки уже нарисованы раньше.
        """
        if self.last:
            last_rect = pygame.Rect(self.last, CELL_SIZE)
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        self.draw_cell(self.get_head_position(), self.body_color)


def handle_keys(game_object):
    """Смотрит, какие кнопки нажали, и меняет направление змейки.

    Стрелки меняют направление. Esc или закрытие окна выходят из игры.

    Args:
        game_object: змейка, у которой меняем next_direction.

    Raises:
        SystemExit: если закрыли окно или нажали Esc.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE):
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            current = game_object.next_direction or game_object.direction
            game_object.next_direction = KEY_TO_DIRECTION.get(
                (event.key, current), current
            )


def main():
    """Запускает игру.

    Создаем змейку и яблоко. Потом в цикле: читаем клавиши, двигаем
    змейку, проверяем, съела ли она яблоко и не укусила ли себя,
    и рисуем всё заново. Выход — закрыть окно или нажать Esc.
    """
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    record_length = snake.length
    pygame.display.set_caption(f'Змейка | Рекорд: {record_length}')
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            if snake.length > record_length:
                record_length = snake.length
                pygame.display.set_caption(
                    f'Змейка | Рекорд: {record_length}'
                )

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
