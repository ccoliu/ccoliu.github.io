import random


def generate_maze(width, height):
    maze = [["#" for _ in range(width)] for _ in range(height)]
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def is_valid_move(x, y):
        return 0 <= x < width and 0 <= y < height and maze[y][x] == " "

    def create_maze(x, y):
        maze[y][x] = " "
        random.shuffle(directions)
        for dx, dy in directions:
            next_x, next_y = x + 2 * dx, y + 2 * dy
            if is_valid_move(next_x, next_y):
                maze[y + dy][x + dx] = " "
                create_maze(next_x, next_y)

    create_maze(1, 1)  # Start generation from (1, 1)

    return maze


def print_maze(maze, player_x, player_y):
    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            if x == player_x and y == player_y:
                print("P", end="")
            else:
                print(char, end="")
        print()


def move_player(maze, x, y, direction):
    if direction == 'up':
        if y > 0 and maze[y - 1][x] == ' ':
            y -= 1
    elif direction == 'down':
        if y < len(maze) - 1 and maze[y + 1][x] == ' ':
            y += 1
    elif direction == 'left':
        if x > 0 and maze[y][x - 1] == ' ':
            x -= 1
    elif direction == 'right':
        if x < len(maze[0]) - 1 and maze[y][x + 1] == ' ':
            x += 1

    return x, y


def detect_collision(maze, x, y):
    return maze[y][x] != ' '  # True if there is a collision


def check_game_completion(maze, x, y):
    return y == len(maze) - 2 and x == len(maze[0]) - 2


maze = generate_maze(21, 21)
player_x, player_y = 1, 1

while True:
    print_maze(maze, player_x, player_y)
    user_input = input("Use arrow keys to move (↑, ↓, ←, →): ")

    if user_input == '\x1b[A':  # Up arrow
        direction = 'up'
    elif user_input == '\x1b[B':  # Down arrow
        direction = 'down'
    elif user_input == '\x1b[C':  # Right arrow
        direction = 'right'
    elif user_input == '\x1b[D':  # Left arrow
        direction = 'left'
    else:
        direction = None

    if direction:
        new_player_x, new_player_y = move_player(maze, player_x, player_y, direction)

        if not detect_collision(maze, new_player_x, new_player_y):
            player_x, player_y = new_player_x, new_player_y

            if check_game_completion(maze, player_x, player_y):
                print("Congratulations! You have reached the end of the maze.")
                break
