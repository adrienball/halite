import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move
import math
import os

MAX_STRENGTH = 255

SOUTH_EAST, SOUTH_WEST, NORTH_WEST, NORTH_EAST = range(5, 9)
CARDINAL_DIRECTIONS = {NORTH, EAST, SOUTH, WEST}


def get_best_individual_move(square, available_directions=CARDINAL_DIRECTIONS):
    if len(available_directions) == 0:
        return Move(square, STILL)

    if len(available_directions) > 1:
        diagonal_directions = get_diagonal_directions(available_directions)
        all_directions = available_directions.union(diagonal_directions)

        best_opportunity_direction = max(
            all_directions,
            key=lambda d: move_opportunity(square, d))

        if is_diagonal_direction(best_opportunity_direction):
            best_opportunity_direction = get_best_path_direction(
                square, best_opportunity_direction)
    else:
        best_opportunity_direction = list(available_directions)[0]

    target_square = game_map.get_target(square, best_opportunity_direction)

    if target_square.owner == myID and square.strength <= 5 * square.production:
        return Move(square, STILL)

    if is_move_possible(square, target_square):
        return Move(square, best_opportunity_direction)
    else:
        return Move(square, STILL)


def get_best_path_direction(square, direction):
    cardinal_directions = get_cardinal_directions(direction)
    targets = [game_map.get_target(square, d) for d in cardinal_directions]
    strengths = [-(MAX_STRENGTH - t.strength) if t.owner == myID else t.strength
                 for t in targets]
    if strengths[0] < strengths[1]:
        return cardinal_directions[0]
    else:
        return cardinal_directions[1]


def get_diagonal_directions(directions):
    diag_directions = set()
    if SOUTH in directions:
        if EAST in directions:
            diag_directions.add(SOUTH_EAST)
        if WEST in directions:
            diag_directions.add(SOUTH_WEST)
    if NORTH in directions:
        if EAST in directions:
            diag_directions.add(NORTH_EAST)
        if WEST in directions:
            diag_directions.add(NORTH_WEST)
    return diag_directions


def get_cardinal_directions(diagonal_direction):
    if diagonal_direction == SOUTH_WEST:
        return [SOUTH, WEST]
    if diagonal_direction == SOUTH_EAST:
        return [SOUTH, EAST]
    if diagonal_direction == NORTH_EAST:
        return [NORTH, EAST]
    if diagonal_direction == NORTH_WEST:
        return [NORTH, WEST]


def is_diagonal_direction(direction):
    return direction >= 5


def get_target(square, direction):
    if is_diagonal_direction(direction):
        return get_target_diagonal(square, direction)
    else:
        return game_map.get_target(square, direction)


def get_target_diagonal(square, direction):
    if direction == SOUTH_WEST:
        target = game_map.get_target(square, SOUTH)
        target = game_map.get_target(target, WEST)
        return target
    if direction == SOUTH_EAST:
        target = game_map.get_target(square, SOUTH)
        target = game_map.get_target(target, EAST)
        return target
    if direction == NORTH_EAST:
        target = game_map.get_target(square, NORTH)
        target = game_map.get_target(target, EAST)
        return target
    if direction == NORTH_WEST:
        target = game_map.get_target(square, NORTH)
        target = game_map.get_target(target, WEST)
        return target


def is_direction_possible(source_square, direction):
    target = game_map.get_target(source_square, direction)
    return is_move_possible(source_square, target)


def is_move_possible(source_square, target_square):
    if target_square.owner == myID:
        return True
    elif target_square.owner == unowned_id:
        return source_square.strength > target_square.strength
    else:
        return source_square.strength >= target_square.strength


def square_opportunity(square):
    normalized_strength = square.strength / MAX_STRENGTH
    normalized_production = square.production / MAX_PRODUCTION
    opportunity = normalized_production * ((1 - normalized_strength) ** 3)
    opportunity_factor = get_opportunity_factor(square.owner)
    return opportunity_factor * opportunity


def move_opportunity(square, direction):
    """
    :return: a float that represents the opportunity of moving to `direction`
    from `square`
    """
    is_diagonal = is_diagonal_direction(direction)
    opportunity = 0
    current_weight = 1
    decay_factor = math.exp(-1 / 2.0)
    if is_diagonal:
        decay_factor **= 2
    current_square = square
    max_width = min(game_map.width, 45)
    horizon = max_width / 4 if is_diagonal else max_width / 2

    for i in range(int(horizon)):
        neighbor = get_target(current_square, direction)
        overkill_factor = 1.0
        if i == 0 and not is_diagonal:
            overkill_factor = get_overkill_factor(current_square, neighbor)
        opportunity += overkill_factor * square_opportunity(neighbor) \
                       * current_weight
        current_square = neighbor
        current_weight *= decay_factor
    return opportunity


def get_opportunity_factor(square_owner):
    if square_owner == myID:
        return 0.0
    elif square_owner == unowned_id:
        return 1.0
    elif number_of_enemy_bots == 1:
        return 1.2
    else:
        return 0.7


def get_overkill_factor(source_square, target_square):
    neighbors = game_map.neighbors(target_square, n=1, include_self=True)
    enemies = filter(lambda s: s.owner != myID and s.owner != unowned_id,
                     neighbors)
    total_damage = 0
    for s in enemies:
        total_damage += min(source_square.strength, s.strength)
    min_damage = min(source_square.strength, target_square.strength)
    overkill_damage = total_damage - min_damage
    return 1 + overkill_damage / MAX_STRENGTH


def get_number_of_enemy_bots():
    owners = set([square.owner for square in game_map])
    return len(owners) - 2


def get_best_collective_moves():
    """
    Compute the best collective moves by processing the stack of best individual
    moves and re-affecting self-destructive moves, i.e. moves that have a
    cumulative strength > MAX_STRENGTH.
    :return: a list of moves that are collectively optimized
    """

    targets = [[None for j in range(game_map.width)] for i in
               range(game_map.height)]
    squares_stack = [
        {'square': square, 'available_directions': {NORTH, EAST, SOUTH, WEST}}
        for square in game_map if
        square.owner == myID]

    while len(squares_stack) > 0:
        squares_stack_item = squares_stack.pop()
        square = squares_stack_item['square']
        available_directions = squares_stack_item['available_directions']
        move = get_best_individual_move(square, available_directions)
        target = game_map.get_target(square, move.direction)

        if targets[target.y][target.x] is None:
            targets[target.y][target.x] = [{
                'move': move,
                'available_directions': available_directions
            }]
        else:
            cumulated_moves = list(targets[target.y][target.x])
            cumulated_moves += [{
                'move': move,
                'available_directions': available_directions
            }]
            if sum([m['move'].square.strength for m in
                    cumulated_moves]) <= MAX_STRENGTH * 1.2:
                targets[target.y][target.x] = cumulated_moves
            else:
                cumulated_moves.sort(
                    key=lambda item: -1000 if item['move'].direction == STILL
                    else -item['move'].square.strength)
                total_strength = 0
                top_moves = []
                for mv in cumulated_moves:
                    strength = mv['move'].square.strength
                    if total_strength + strength <= MAX_STRENGTH:
                        total_strength += strength
                        top_moves.append(mv)
                    else:
                        directions = mv['available_directions']
                        directions.remove(mv['move'].direction)
                        squares_stack.append({
                            'square': mv['move'].square,
                            'available_directions': directions
                        })
                targets[target.y][target.x] = top_moves

    moves = []
    for row in targets:
        for site in row:
            if site is not None:
                moves += [mv['move'] for mv in site]

    return moves


myID, game_map = hlt.get_init()
productions = [sq.production for sq in game_map]
MAX_PRODUCTION = max(productions)
unowned_id = 0
bot_name = os.path.basename(__file__).split('.')[0]
hlt.send_init(bot_name)

while True:
    game_map.get_frame()
    number_of_enemy_bots = get_number_of_enemy_bots()
    moves = get_best_collective_moves()
    hlt.send_frame(moves)
