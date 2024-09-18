def find_player_position(map):
    return map.index(-1)

def move_player(direction, map, map_size):
    player_pos = find_player_position(map)

    if direction == 'ArrowUp':
        new_pos = player_pos - map_size if player_pos >= map_size else player_pos
    elif direction == 'ArrowDown':
        new_pos = player_pos + map_size if player_pos < len(map) - map_size else player_pos
    elif direction == 'ArrowLeft':
        new_pos = player_pos - 1 if player_pos % map_size != 0 else player_pos
    elif direction == 'ArrowRight':
        new_pos = player_pos + 1 if (player_pos + 1) % map_size != 0 else player_pos
    else:
        new_pos = player_pos

    if map[new_pos] == 0:
        map[player_pos] = 0
        map[new_pos] = -1
    elif map[new_pos] == 3:
        map[player_pos] = 0
        map[new_pos] = -2


def change_door(map):
    if isinstance(map, list) and 2 in map:
        i = map.index(2)
        map[i] = -1
    else:
        print("Error: map no es una lista o no contiene el valor 2")