import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random
import math

myID, game_map = hlt.get_init()
productions = [square.production for square in game_map]
max_production = max(productions)
hlt.send_init("ChallengerBot")


def assign_move(square):
    if square.strength == 0:
        return Move(square, STILL)

    directions_with_opportunity = [{"direction": direction, "opportunity": direction_opportunity(square, direction)}
                                   for direction in [NORTH, EAST, SOUTH, WEST, STILL]]
    directions_with_opportunity.sort(key=lambda item: -item["opportunity"])

    best_opportunity_direction = directions_with_opportunity[0]["direction"]
    target_square = game_map.get_target(square, best_opportunity_direction)

    if is_move_possible(square, target_square):
        return Move(square, best_opportunity_direction)
    else:
        return Move(square, STILL)


def is_move_possible(source_square, target_square):
    return target_square.owner == myID or source_square.strength >= target_square.strength


def direction_opportunity(square, direction):
    if direction == STILL:
        return still_opportunity(square)
    else:
        return move_opportunity(square, direction)


# TODO: improve opportunity definition by taking into account distance to frontier
def still_opportunity(square):
    return square_opportunity(square.strength, square.production)


def square_opportunity(strength, production):
    normalized_strength = strength / 255
    normalized_production = (production + 1) / (max_production + 1)
    return 1 - normalized_strength / normalized_production


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


while True:
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
