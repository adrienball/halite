import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
from itertools import groupby
import math
import os


def assign_move(square):
    if square.strength <= 5 * square.production:
        return Move(square, STILL)

    directions_with_opportunity = [
        {"direction": direction, "opportunity": direction_opportunity(square, direction)}
        for direction in [NORTH, EAST, SOUTH, WEST]
        ]
    directions_with_opportunity.sort(key=lambda item: -item["opportunity"])

    best_opportunity_direction = directions_with_opportunity[0]["direction"]
    target_square = game_map.get_target(square, best_opportunity_direction)

    if is_move_possible(square, target_square):
        return Move(square, best_opportunity_direction)
    else:
        return Move(square, STILL)


def find_nearest_enemy_direction(square):
    direction = NORTH
    max_distance = min(game_map.width, game_map.height) / 2
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        while current.owner == myID and distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)
        if distance < max_distance:
            direction = d
            max_distance = distance
    return direction


def distance_to_enemy(square, direction):
    distance = 0
    max_distance = min(game_map.width, game_map.height) / 2
    current = square
    while current.owner == myID and distance < max_distance:
        distance += 1
        current = game_map.get_target(current, direction)
    return distance


def is_move_possible(source_square, target_square):
    if target_square.owner == myID:
        return True
    if target_square.owner == unowned_id:
        return source_square.strength > target_square.strength
    else:
        return source_square.strength >= target_square.strength


def direction_opportunity(square, direction):
    if direction == STILL:
        return still_opportunity(square)
    else:
        return move_opportunity(square, direction)


# TODO: improve opportunity definition by taking into account distance to frontier
def still_opportunity(square):
    # distances = [distance_to_enemy(square, direction) for direction in (NORTH, EAST, SOUTH, WEST)]
    # frontier_distance = max(distances)
    # max_distance = min(game_map.width, game_map.height) / 2
    return square_opportunity(square.strength, square.production)  # * (1 - frontier_distance / max_distance)


def square_opportunity(strength, production):
    normalized_strength = (strength + 1) / 256
    normalized_production = (production + 1) / (max_production + 1)
    opportunity = normalized_production / normalized_strength
    return opportunity


def move_opportunity(square, direction):
    # TODO: this can be simplified by computing the closed form of the sums
    # distance = distance_to_enemy(square, direction)
    max_distance = min(game_map.width, game_map.height) / 2
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
    return (opportunity / total_weight)  # * (1 - distance / max_distance)


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
