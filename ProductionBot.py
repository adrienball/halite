import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
from itertools import groupby
import os
import math


def assign_move(square):
    if square.strength == 0:
        return Move(square, STILL)

    directions_with_opportunity = [
        {"direction": direction, "opportunity": expected_move_production(square, direction)}
        for direction in [NORTH, EAST, SOUTH, WEST]
        ]
    directions_with_opportunity.sort(key=lambda item: -item["opportunity"])

    best_opportunity = directions_with_opportunity[0]
    if best_opportunity["opportunity"] <= 2:
        return Move(square, STILL)

    best_opportunity_direction = best_opportunity["direction"]
    target_square = game_map.get_target(square, best_opportunity_direction)

    if is_move_possible(square, target_square):
        return Move(square, best_opportunity_direction)
    else:
        return Move(square, STILL)


def is_move_possible(source_square, target_square):
    if target_square.owner == myID:
        return True
    if target_square.owner == unowned_id:
        return source_square.strength > target_square.strength
    else:
        return source_square.strength >= target_square.strength


def direction_opportunity(square, direction):
    return move_opportunity(square, direction)


def square_opportunity(strength, production):
    normalized_strength = (strength + 1) / 256
    normalized_production = (production + 1) / (max_production + 1)
    opportunity = normalized_production / normalized_strength
    return opportunity


def move_opportunity(square, direction):
    # TODO: this can be simplified by computing the closed form of the sums
    opportunity = 0
    current_weight = 1
    decay_factor = math.exp(-1 / 2.0)
    total_weight = 0
    current_square = square

    for i in range(game_map.width):
        neighbor = game_map.get_target(current_square, direction)
        if neighbor.owner != myID:
            opportunity += square_opportunity(neighbor.strength, neighbor.production) * current_weight
        current_square = neighbor
        total_weight += current_weight
        current_weight *= decay_factor
    return opportunity / total_weight


def expected_move_production(square, direction):
    current_strength = square.strength
    current_production = 0
    neighbor = square
    decay = 1
    decay_factor = math.exp(-1 / 5.0)
    for i in range(int(game_map.width / 2)):
        current_square = neighbor
        neighbor = game_map.get_target(current_square, direction)
        if neighbor.owner == myID:
            current_strength = min(255, current_strength + neighbor.strength)
        else:
            if current_strength > neighbor.strength:
                current_strength -= neighbor.strength
                current_production += neighbor.production * decay
            else:
                break
        decay *= decay_factor
    return current_production


def get_unowned_id():
    owners = [square.owner for square in game_map]
    max_owner_id = myID
    max_owner_count = 0
    for owner_id, owners in groupby(owners, lambda x: x):
        n = len(list(owners))
        if n > max_owner_count:
            max_owner_count = n
            max_owner_id = owner_id
    return max_owner_id


myID, game_map = hlt.get_init()
productions = [square.production for square in game_map]
max_production = max(productions)
unowned_id = get_unowned_id()
bot_name = os.path.basename(__file__).split('.')[0]
hlt.send_init(bot_name)

while True:
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
