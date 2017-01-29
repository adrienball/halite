import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move
from itertools import groupby
import math
import os
import logging

MAX_STRENGTH = 255

logging.basicConfig(filename='debug.log', level=logging.DEBUG)


def get_best_individual_move(square, available_directions={NORTH, EAST, SOUTH, WEST}):
    if len(available_directions) == 0 or square.strength <= 5 * square.production:
        return Move(square, STILL)

    best_opportunity_square = max(game_map.neighbors(square, n=20),
                                  key=lambda s: target_opportunity(source_square=square, target_square=s))

    directions = [d for d in get_directions(square, best_opportunity_square) if d in available_directions]
    for direction in list(directions):
        if is_direction_possible(square, direction):
            return Move(square, direction)
    return Move(square, STILL)


def get_directions(source_square, target_square):
    delta_y = target_square.y - source_square.y
    delta_x = target_square.x - source_square.x
    if delta_y == 0:
        return [EAST] if delta_x > 0 else [WEST]
    if delta_x == 0:
        return [SOUTH] if delta_y > 0 else [NORTH]

    if delta_y > 0:
        # Moving SOUTH
        if delta_x > 0:
            # Moving EAST
            return [SOUTH, EAST] if abs(delta_y) > abs(delta_x) else [EAST, SOUTH]
        else:
            # Moving WEST
            return [SOUTH, WEST] if abs(delta_y) > abs(delta_x) else [WEST, SOUTH]
    else:
        # Moving NORTH
        if delta_x > 0:
            # Moving EAST
            return [NORTH, EAST] if abs(delta_y) > abs(delta_x) else [EAST, NORTH]
        else:
            # Moving WEST
            return [NORTH, WEST] if abs(delta_y) > abs(delta_x) else [WEST, NORTH]


def is_direction_possible(source_square, direction):
    return is_move_possible(source_square, game_map.get_target(source_square, direction))


def is_move_possible(source_square, target_square):
    if target_square.owner == myID:
        return True
    if target_square.owner == unowned_id:
        return source_square.strength > target_square.strength
    else:
        return source_square.strength >= target_square.strength


def target_opportunity(source_square, target_square):
    normalized_strength = (target_square.strength + 1) / (MAX_STRENGTH + 1)
    normalized_production = (target_square.production + 1) / (MAX_PRODUCTION + 1)
    opportunity = normalized_production / normalized_strength
    opportunity_factor = get_opportunity_factor(target_square.owner)
    distance_factor = get_distance_factor(source_square, target_square)
    return opportunity * opportunity_factor * distance_factor


def get_opportunity_factor(square_owner):
    if square_owner == myID:
        return 0.0
    elif square_owner == unowned_id:
        return 1.0
    elif number_of_enemy_bots == 1:
        return 1.2
    else:
        return 0.7


def get_distance_factor(source_square, target_square):
    distance = game_map.get_distance(source_square, target_square)
    distance_factor = math.exp(-distance / 2.0)
    return distance_factor


def get_number_of_enemy_bots():
    owners = set([square.owner for square in game_map])
    return len(owners) - 2


def get_unowned_id():
    """
    :return: the id of unowned squares
    """
    owners = [square.owner for square in game_map]
    max_owner_id = myID
    max_owner_count = 0
    for owner_id, owners in groupby(owners, lambda x: x):
        n = len(list(owners))
        if n > max_owner_count:
            max_owner_count = n
            max_owner_id = owner_id
    return max_owner_id


def get_best_collective_moves():
    """
    Compute the best collective moves by processing the stack of best individual moves and re-affecting
    self-destructive moves, i.e. moves that have a cumulative strength > MAX_STRENGTH.
    :return: a list of moves that are collectively optimized
    """

    # TODO: Replace dictionary with matrix here
    targets = {}
    squares_stack = [{'square': square, 'available_directions': {NORTH, EAST, SOUTH, WEST}} for square in game_map if
                     square.owner == myID]

    while len(squares_stack) > 0:
        squares_stack_item = squares_stack.pop()
        square = squares_stack_item['square']
        available_directions = squares_stack_item['available_directions']
        move = get_best_individual_move(square, available_directions)
        target = game_map.get_target(square, move.direction)
        target_key = "{},{}".format(target.x, target.y)
        if target_key not in targets:
            targets[target_key] = [{'move': move, 'available_directions': available_directions}]
        else:
            existing_moves = targets[target_key]
            cumulated_moves = existing_moves + [{'move': move, 'available_directions': available_directions}]
            if sum([m['move'].square.strength for m in cumulated_moves]) <= MAX_STRENGTH * 1.2:
                targets[target_key] = existing_moves + [{'move': move, 'available_directions': available_directions}]
            else:
                if move.direction == STILL:
                    targets[target_key] = [{'move': move, 'available_directions': {}}]
                    for existing_move in existing_moves:
                        directions = existing_move['available_directions']
                        directions.remove(existing_move['move'].direction)
                        squares_stack.append(
                            {'square': existing_move['move'].square, 'available_directions': directions})
                else:
                    # sorting existing moves by decreasing strength
                    cumulated_moves.sort(
                        key=lambda item: -1000 if item['move'].direction == STILL else -item['move'].square.strength)
                    total_strength = 0
                    top_moves = []
                    for mv in cumulated_moves:
                        strength = mv['move'].square.strength
                        if total_strength + strength <= 255:
                            total_strength += strength
                            top_moves.append(mv)
                        else:
                            directions = mv['available_directions']
                            directions.remove(mv['move'].direction)
                            squares_stack.append({'square': mv['move'].square, 'available_directions': directions})
                    targets[target_key] = top_moves
    moves = [target_move['move'] for target_moves in targets.values() for target_move in target_moves]
    return moves


myID, game_map = hlt.get_init()
productions = [sq.production for sq in game_map]
MAX_PRODUCTION = max(productions)
unowned_id = get_unowned_id()
bot_name = os.path.basename(__file__).split('.')[0]
hlt.send_init(bot_name)

while True:
    game_map.get_frame()
    number_of_enemy_bots = get_number_of_enemy_bots()
    best_collective_moves = get_best_collective_moves()
    hlt.send_frame(best_collective_moves)
