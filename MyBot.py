import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random
import math
import logging

myID, game_map = hlt.get_init()
# logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)
hlt.send_init("MyPythonBot")


# strengths_and_productions = [[square.strength, square.production] for square in game_map]
# logging.debug(strengths_and_productions)


def assign_move(square):
    if square.strength == 0:
        return Move(square, STILL)

    sorted_moves = [NORTH, EAST, SOUTH, WEST]
    sorted_moves.sort(key=lambda move: -direction_opportunity(square, move))

    target_square = game_map.get_target(square, sorted_moves[0])

    if is_move_possible(square, target_square):
        return Move(square, sorted_moves[0])
    else:
        return Move(square, STILL)


def is_move_possible(source_square, target_square):
    return target_square.owner == myID or source_square.strength >= target_square.strength


def direction_opportunity(square, direction):
    opportunity = 0
    decay = 1
    decay_factor = math.exp(-1 / 2.0)
    current_square = square
    for i in range(game_map.width):
        neighbor = game_map.get_target(current_square, direction)
        if neighbor.owner != myID:
            opportunity += (neighbor.production / (neighbor.strength + 1)) * decay
        current_square = neighbor
        decay *= decay_factor
    return opportunity


while True:
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
