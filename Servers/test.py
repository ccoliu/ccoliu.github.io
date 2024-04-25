# Maze Game

# Define the maze
maze = [
    [' ', ' ', ' ', 'X', ' ', ' '],
    [' ', 'X', ' ', 'X', ' ', 'X'],
    ['P', 'X', ' ', ' ', ' ', ' '],
    [' ', 'X', 'X', 'X', ' ', ' '],
    [' ', ' ', ' ', 'X', ' ', 'X'],
]

# Player starting position
player_pos = [2, 0]

# Game loop
while True:
    for row in maze:
        print(''.join(row))

    move = input("Enter WASD controls to move (or Q to quit): ").upper()

    if move == 'Q':
        print("Quitting game. Goodbye!")
        break

    new_pos = player_pos.copy()

    if move == 'W':
        new_pos[0] -= 1
    elif move == 'A':
        new_pos[1] -= 1
    elif move == 'S':
        new_pos[0] += 1
    elif move == 'D':
        new_pos[1] += 1

    if (
        0 <= new_pos[0] < len(maze)
        and 0 <= new_pos[1] < len(maze[0])
        and maze[new_pos[0]][new_pos[1]] != 'X'
    ):
        maze[player_pos[0]][player_pos[1]] = ' '
        player_pos = new_pos
        if maze[player_pos[0]][player_pos[1]] == ' ':
            maze[player_pos[0]][player_pos[1]] = 'P'
    else:
        print("Invalid move. Try again.")
