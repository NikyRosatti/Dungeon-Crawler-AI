mapa_original = [
    -1, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 1, 1, 0,
    0, 1, 0, 0, 1, 0, 0,
    0, 1, 0, 0, 1, 0, 1,
    0, 0, 0, 0, 0, 0, 1,
    0, 1, 0, 0, 1, 0, 1,
    0, 0, 0, 1, 1, 0, 3,
]

map_size = 7

def find_player_position():
    return mapa_original.index(-1)

def move_player(direction):
    global mapa_original
    player_pos = find_player_position()

    if direction == 'ArrowUp':
        new_pos = player_pos - map_size if player_pos >= map_size else player_pos
    elif direction == 'ArrowDown':
        new_pos = player_pos + map_size if player_pos < len(mapa_original) - map_size else player_pos
    elif direction == 'ArrowLeft':
        new_pos = player_pos - 1 if player_pos % map_size != 0 else player_pos
    elif direction == 'ArrowRight':
        new_pos = player_pos + 1 if (player_pos + 1) % map_size != 0 else player_pos
    else:
        new_pos = player_pos

    if mapa_original[new_pos] == 0:
        mapa_original[player_pos] = 0
        mapa_original[new_pos] = -1
    elif mapa_original[new_pos] == 3:
        mapa_original[player_pos] = 0
        mapa_original[new_pos] = -2
