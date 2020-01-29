from collections import namedtuple, defaultdict
import heapq
import os.path
import pickle
# import time

GameState = namedtuple('GameState', 'to_move, utility, board, moves')
FOUR_CORNERS = (0, 15, 240, 255)
UPPER_HORIZONTAL = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
LOWER_HORIZONTAL = (241, 242, 243, 244, 245, 246, 247,
                    248, 249, 250, 251, 252, 253, 254)
LEFT_VERTICAL = (16, 32, 48, 64, 80, 96, 112, 128,
                 144, 160, 176, 192, 208, 224)
RIGHT_VERTICAL = (31, 47, 63, 79, 95, 111, 127,
                  143, 159, 175, 191, 207, 223, 239)
WHITE_ZONE = (251, 252, 253, 254, 255, 235, 236, 237, 238,
              239, 220, 221, 222, 223, 205, 206, 207, 190, 191)
BLACK_ZONE = (0, 1, 2, 3, 4, 16, 17, 18, 19, 20,
              32, 33, 34, 35, 48, 49, 50, 64, 65)
NO_ZONE = (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 40, 41, 42, 43, 44, 45, 46, 47, 57, 58, 59, 60, 61, 62, 63, 73, 74, 75, 76, 77, 78, 79, 90, 91, 92, 93, 94, 95, 109, 110, 111, 125, 126, 127, 142, 143, 158, 159, 240, 241, 242,
           243, 244, 245, 246, 247, 248, 249, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 208, 209, 210, 211, 212, 213, 214, 215, 192, 193, 194, 195, 196, 197, 198, 176, 177, 178, 179, 180, 181, 182, 160, 161, 162, 163, 164, 165, 144, 145, 146, 128, 129, 130, 112, 113, 96, 97)
B_START = {1: (17, 51), 2: (2, 36), 3: (35, 37), 4: (34, 68), 5: (0, 66), 6: (1, 69), 7: (4, 21), 8: (65, 81), 9: (64, 98), 10: (
    50, 86), 11: (3, 99), 12: (48, 84), 13: (16, 116), 14: (32, 38), 15: (18, 114), 16: (33, 131), 17: (49, 147), 18: (20, 82), 19: (19, 53)}
W_START = {1: (238, 204), 2: (253, 219), 3: (220, 218), 4: (221, 187), 5: (255, 189), 6: (254, 186), 7: (251, 234), 8: (190, 174), 9: (191, 157), 10: (
    205, 169), 11: (252, 156), 12: (207, 171), 13: (239, 139), 14: (223, 217), 15: (237, 141), 16: (222, 124), 17: (206, 108), 18: (235, 173), 19: (236, 202)}


def execute():
    """read input"""
    input_data = get_input_file('input.txt')
    team_color = input_data[1]
    i = 0
    board = [' ' for x in range(256)]
    for x in range(3, len(input_data)):
        for y in range(len(input_data[3])):
            board[i] = input_data[x][y]
            i += 1
    game_mode = input_data[0]
    team_color = input_data[1]
    play_time = input_data[2]
    """check playdata"""
    nth_move = 20
    if os.path.exists('playdata.txt'):
        with open('playdata.txt', 'rb') as outputFile:
            nth_move = pickle.load(outputFile)
            nth_move += 1
    else:
        nth_move = 1
    """initialize the game"""
    game = Halma(board, 0, team_color)
    state = game.initial
    depth = 2
    comp_move = ()
    """if time is less than 3s"""
    if float(play_time) < 3.00:
        ret = ''
        comp_move = game.actions(state)[0]
        if abs(comp_move[1]-comp_move[0]) in (1, 15, 16, 17):
            ret += convert_to_2d('E', comp_move)
        else:
            for key, value in game.jump_moves_output.items():
                if key == comp_move[0]:
                    jump_move = get_jump_moves(value, comp_move[1])
                    break
            for j in jump_move:
                ret += convert_to_2d('J', j)
        output_file(ret, 'output.txt')
        return
    """compute comp_move"""
    if nth_move < 20:
        comp_move = W_START[nth_move] if team_color == 'WHITE' else B_START[nth_move]
        try:
            with open('playdata.txt', 'wb') as outputFile:
                pickle.dump(nth_move, outputFile)
        except IOError as err:
            print('File error: ' + str(err))
    else:
        comp_move = minimax(state, game, depth)
    """write result to output.txt"""
    ret = ''
    if abs(comp_move[1]-comp_move[0]) in (1, 15, 16, 17):
        ret += convert_to_2d('E', comp_move)
    else:
        for key, value in game.jump_moves_output.items():
            if key == comp_move[0]:
                jump_move = get_jump_moves(value, comp_move[1])
                break
        for j in jump_move:
            ret += convert_to_2d('J', j)
    output_file(ret, 'output.txt')


def get_jump_moves(value, target):
    ret = []
    return get_jump_moves_helper(ret, True, value, target)


def get_jump_moves_helper(ret, flag, value, target):
    if not flag:
        return ret
    for v in value:
        if v[1] == target and tuple(reversed(v)) not in ret:
            ret.insert(0, v)
            target = v[0]
            flag = True
            break
        else:
            flag = False
    return get_jump_moves_helper(ret, flag, value, target)


def convert_to_2d(letter, move):
    res = letter+' '
    for each in move:
        h = each//16
        w = each-(16*h)
        res += str(w)+','+str(h)+' '
    res += '\n'
    return res


def get_input_file(filename):
    input = []
    try:
        with open(filename) as f:
            line = f.readline()
            while line:
                input.append(line.strip())
                line = f.readline()
        return input
    except IOError as err:
        print('File error: ' + str(err))


def output_file(ret, filename):
    try:
        with open(filename, 'w+') as outputFile:
            outputFile.write(ret)
    except IOError as err:
        print('File error: ' + str(err))


def minimax(state, game, d, cutoff_test=None, eval_fn=None):
    player = state.to_move
    turn_to_move = ('W' if state.to_move == 'B' else 'B')
    opposite_zone = WHITE_ZONE if player == 'B' else BLACK_ZONE

    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -100000
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a, turn_to_move),
                                 alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = 100000
        for a in game.actions(state):
            v = min(v, max_value(game.result(
                state, a, turn_to_move), alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    cutoff_test = (cutoff_test or
                   (lambda state, depth: depth > d or
                    game.terminal_test(state, player)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -1000000
    beta = 1000000
    best_action = ()
    test = []
    for a in game.actions(state):
        v = 0
        v = min_value(game.result(state, a, turn_to_move), best_score, beta, 1)
        test.append((a, v))
        if v >= best_score:
            if v == best_score:
                checklist = []
                # print('v: ', v, best_score)
                for i in opposite_zone:
                    if state.board[i] == player:
                        checklist.append(i)
                if a[1] not in checklist and len(checklist) == 18:
                    if a[1] in opposite_zone:
                        best_score = v
                        best_action = a
                else:
                    for i in opposite_zone:
                        if state.board[i] == '.' and abs(a[1]-i) < abs(best_action[1]-i):
                            best_score = v
                            best_action = a
                            break
            else:
                best_score = v
                best_action = a
    return best_action


class Halma:
    def __init__(self, board, util, team_color):
        self.board = board
        player = 'W' if team_color == 'WHITE' else 'B'
        self.jump_moves_output = defaultdict(list)
        self.initial = GameState(
            to_move=player, utility=0, board=board, moves=self.get_combined_moves(board, player))

    def actions(self, state):
        """list of allowable moves"""
        """if there are moves inside zone, moves that start outside zone get removed"""
        """2nd rule: once in goal zone, end move have to still in the zone"""
        """3rd rule: once out of camp, can't end in own camp"""
        moves_inside = []
        moves_outside = []
        moves_outside_extra = []
        moves_inside_to_outside = []
        outside_flag = True
        zone = WHITE_ZONE if state.to_move == 'W' else BLACK_ZONE
        opposing_zone = BLACK_ZONE if state.to_move == 'W' else WHITE_ZONE
        # print('ac: ', state.to_move)
        for move in state.moves:
            if state.to_move == 'B' and move[0] in zone:
                if move[1] not in zone:
                    moves_inside_to_outside.append(move)
                    outside_flag = False
                elif move[1] > move[0] and move[1]-15 != move[0] and move[1]-30 != move[0]:
                    moves_inside.append(move)
                    outside_flag = False
                else:
                    continue
            elif state.to_move == 'W' and move[0] in zone:
                if move[1] not in zone:
                    moves_inside_to_outside.append(move)
                    outside_flag = False
                elif move[1] < move[0] and move[1]+15 != move[0] and move[1]+30 != move[0]:
                    moves_inside.append(move)
                    outside_flag = False
                else:
                    continue
            elif outside_flag and move[0] not in zone and move[1] not in zone:
                if move[0] in opposing_zone and move[1] not in opposing_zone:
                    continue
                else:
                    if state.to_move == 'W' and move[0] > move[1] and move[1] not in NO_ZONE:
                        moves_outside.append(move)
                    elif state.to_move == 'B' and move[1] > move[0] and move[1] not in NO_ZONE:
                        moves_outside.append(move)
                    else:
                        moves_outside_extra.append(move)
            else:
                continue
        if moves_inside_to_outside:
            if len(moves_inside_to_outside) > 10:
                inout_sorted = sorted(moves_inside_to_outside, key=lambda moves: abs(
                    moves[1]-moves[0]), reverse=True)
                return inout_sorted[:int(len(inout_sorted)/2)+(len(inout_sorted) % 2 > 0)]
            return moves_inside_to_outside
        if moves_inside:
            if len(moves_inside) > 10:
                inside_sorted = sorted(moves_inside, key=lambda moves: abs(
                    moves[1]-moves[0]), reverse=True)
                return inside_sorted[:int(len(inside_sorted)/2)+(len(inside_sorted) % 2 > 0)]
            return moves_inside
        if len(moves_outside) > 10:
            adj, jump = [], []
            for i in moves_outside:
                if abs(i[1]-i[0]) in (17, 16, 15):
                    adj.append(i)
                else:
                    jump.append(i)
            adj_sorted = sorted(adj, key=lambda moves: abs(
                moves[1]-moves[0]), reverse=True)
            jump_sorted = sorted(jump, key=lambda moves: abs(
                moves[1]-moves[0]), reverse=True)
            return jump_sorted+adj_sorted[:int(len(adj_sorted)/3)+(len(adj_sorted) % 3 > 0)]
        else:
            return moves_outside+moves_outside_extra

    def is_any_inside(self, state, position, zone):
        if state.board[position] == state.to_move and position in zone:
            return True
        return False

    def result(self, state, position, turn_to_move):
        """the state from making the move"""
        player = state.to_move
        board = [x for x in state.board]
        board[position[0]] = '.'
        board[position[1]] = player
        return GameState(to_move=turn_to_move, utility=self.compute_utility(board, position, player), board=board, moves=self.get_combined_moves(board, turn_to_move))

    def utility(self, state, player):
        return state.utility if player == 'W' else -state.utility

    def terminal_test(self, state, player):
        """A state is terminal if one player wins."""
        return state.utility == -100000 or state.utility == 100000

    def compute_utility(self, board, position, player):
        """If 'W' wins with this move, return 1; if 'B' wins return -1; else return 0."""
        """count number of squares for each team, whoever has LESS in ITS zone WINS"""
        board2d = self.transform_to_2d(board)
        A1, A2, B1, B2, C1, C2, v = 0, 0, 0, 0, 0, 0, 0
        # print('position: ', position, player)
        for h in range(16):
            for w in range(16):
                if board2d[h][w] == 'W':
                    resA = self.get_manhattan_distance(0, h, w)
                    A1 += resA
                    resB = self.get_manhattan_distance(h, h, w)
                    B1 += resB
                    resC = self.get_max_vertical_advance(board2d, h, w, 'W')
                    C1 += resC
                if board2d[h][w] == 'B':
                    resA = self.get_manhattan_distance(15, h, w)
                    A2 += resA
                    resB = self.get_manhattan_distance(h, h, w)
                    B2 += resB
                    resC = self.get_max_vertical_advance(board2d, h, w, 'B')
                    C2 += resC
        v = (0.911*((A2**2)-(A1**2)))+(0.140*((B2**2)-(B1**2)))+(0.388*(C1-C2))
        return v

    def transform_to_2d(self, board):
        temp_board = [[0 for x in range(16)] for y in range(16)]
        i = 0
        for h in range(0, 16):
            for w in range(0, 16):
                temp_board[h][w] = board[i]
                i += 1
        return temp_board

    def get_max_vertical_advance(self, board, h, w, player):
        count = 0
        while True:
            if player == 'W' and h > 0 and w > 0:
                if board[h-1][w-1] != '.':
                    return count
                count += 1
                h -= 1
            elif player == 'B' and h < 15 and w < 15:
                if board[h+1][w+1] != '.':
                    return count
                count += 1
                h += 1
            else:
                break
        return count

    def get_manhattan_distance(self, dest, h, w):
        res = abs(h - dest) + abs(w - dest)
        return res

    def get_combined_moves(self, board, player):
        # get_jump_moves = sorted(self.get_all_jump_moves(board, player), key=lambda jump: abs(jump[1]-jump[0]), reverse=True)
        # print('moves: ', get_jump_moves)
        return self.get_all_jump_moves(board, player)+self.get_all_adj_moves(board, player)

    def get_all_jump_moves(self, board, player):
        """return list of all jump moves"""
        all_moves = []
        heap_moves = []
        for i in range(256):
            """check if next square is occupied"""
            if board[i] == player:
                if self.is_adj_occupied(board, i-1) and i-1 not in FOUR_CORNERS+LEFT_VERTICAL and self.is_next_two_available(board, i-2):
                    heapq.heappush(heap_moves, (i, i, i-2))
                if self.is_adj_occupied(board, i+1) and i+1 not in FOUR_CORNERS+RIGHT_VERTICAL and self.is_next_two_available(board, i+2):
                    heapq.heappush(heap_moves, (i, i, i+2))
                if self.is_adj_occupied(board, i-16) and self.is_next_two_available(board, i-32):
                    heapq.heappush(heap_moves, (i, i, i-32))
                if self.is_adj_occupied(board, i+16) and self.is_next_two_available(board, i+32):
                    heapq.heappush(heap_moves, (i, i, i+32))
                if self.is_adj_occupied(board, i-17) and i-17 not in FOUR_CORNERS+LEFT_VERTICAL and self.is_next_two_available(board, i-34):
                    heapq.heappush(heap_moves, (i, i, i-34))
                if self.is_adj_occupied(board, i+17) and i+17 not in FOUR_CORNERS+RIGHT_VERTICAL and self.is_next_two_available(board, i+34):
                    heapq.heappush(heap_moves, (i, i, i+34))
                if self.is_adj_occupied(board, i-15) and i-15 not in FOUR_CORNERS+RIGHT_VERTICAL and self.is_next_two_available(board, i-30):
                    heapq.heappush(heap_moves, (i, i, i-30))
                if self.is_adj_occupied(board, i+15) and i+15 not in FOUR_CORNERS+LEFT_VERTICAL and self.is_next_two_available(board, i+30):
                    heapq.heappush(heap_moves, (i, i, i+30))
                """check if next jump can jump more and not jumping back"""
                while heap_moves:
                    jump_move = heapq.heappop(heap_moves)
                    i_jump = (jump_move[0], jump_move[2])
                    self.jump_moves_output[i].append(
                        (jump_move[1], jump_move[2]))
                    if i_jump not in all_moves and jump_move[0] != jump_move[2]:
                        all_moves.append(i_jump)
                        jumped = jump_move[2]
                        if self.is_adj_occupied(board, jumped-1) and jumped-1 not in FOUR_CORNERS+LEFT_VERTICAL and self.is_next_two_available(board, jumped-2):
                            heapq.heappush(heap_moves, (i, jumped, jumped-2))
                        if self.is_adj_occupied(board, jumped+1) and jumped+1 not in FOUR_CORNERS+RIGHT_VERTICAL and self.is_next_two_available(board, jumped+2):
                            heapq.heappush(heap_moves, (i, jumped, jumped+2))
                        if self.is_adj_occupied(board, jumped-16) and self.is_next_two_available(board, jumped-32):
                            heapq.heappush(heap_moves, (i, jumped, jumped-32))
                        if self.is_adj_occupied(board, jumped+16) and self.is_next_two_available(board, jumped+32):
                            heapq.heappush(heap_moves, (i, jumped, jumped+32))
                        if self.is_adj_occupied(board, jumped-17) and jumped-17 not in LEFT_VERTICAL+FOUR_CORNERS and self.is_next_two_available(board, jumped-34):
                            heapq.heappush(heap_moves, (i, jumped, jumped-34))
                        if self.is_adj_occupied(board, jumped+17) and jumped+17 not in RIGHT_VERTICAL+FOUR_CORNERS and self.is_next_two_available(board, jumped+34):
                            heapq.heappush(heap_moves, (i, jumped, jumped+34))
                        if self.is_adj_occupied(board, jumped-15) and jumped-15 not in RIGHT_VERTICAL+FOUR_CORNERS and self.is_next_two_available(board, jumped-30):
                            heapq.heappush(heap_moves, (i, jumped, jumped-30))
                        if self.is_adj_occupied(board, jumped+15) and jumped+15 not in LEFT_VERTICAL+FOUR_CORNERS and self.is_next_two_available(board, jumped+30):
                            heapq.heappush(heap_moves, (i, jumped, jumped+30))
        return all_moves

    def is_adj_occupied(self, board, position):
        if position in range(256) and board[position] != '.':
            return True
        return False

    def is_next_two_available(self, board, position):
        if position in range(256) and board[position] == '.':
            return True
        return False

    def get_all_adj_moves(self, board, player):
        """return list of all adjacent moves"""
        all_moves = []
        for i in range(256):
            if board[i] == player:
                if self.is_corner_square(i):
                    if i == 0:
                        all_moves.extend(
                            [(i, x) for x in (1, 16, 17) if x in range(256) and board[x] == '.'])
                    elif i == 15:
                        all_moves.extend(
                            [(i, x) for x in (14, 30, 31) if x in range(256) and board[x] == '.'])
                    elif i == 240:
                        all_moves.extend(
                            [(i, x) for x in (241, 224, 225) if x in range(256) and board[x] == '.'])
                    elif i == 255:
                        all_moves.extend(
                            [(i, x) for x in (254, 238, 239) if x in range(256) and board[x] == '.'])
                    else:
                        continue
                elif self.is_edge_square(i):
                    if i in UPPER_HORIZONTAL:
                        all_moves.extend(
                            [(i, x) for x in (i-1, i+1, i+15, i+16, i+17) if x in range(256) and board[x] == '.'])
                    elif i in LOWER_HORIZONTAL:
                        all_moves.extend(
                            [(i, x) for x in (i-1, i+1, i-15, i-16, i+17) if x in range(256) and board[x] == '.'])
                    elif i in LEFT_VERTICAL:
                        all_moves.extend(
                            [(i, x) for x in (i+1, i-16, i+16, i+17, i-15) if x in range(256) and board[x] == '.'])
                    elif i in RIGHT_VERTICAL:
                        all_moves.extend(
                            [(i, x) for x in (i-1, i-16, i+16, i-17, i+15) if x in range(256) and board[x] == '.'])
                    else:
                        continue
                else:
                    all_moves.extend([(i, x) for x in (
                        i-1, i+1, i-16, i+16, i-17, i+17, i-15, i+15) if x in range(256) and board[x] == '.'])
        return all_moves

    def is_corner_square(self, position):
        if position in (0, 15, 240, 255):
            return True
        return False

    def is_edge_square(self, position):
        if position in (UPPER_HORIZONTAL+LOWER_HORIZONTAL+LEFT_VERTICAL+RIGHT_VERTICAL):
            return True
        return False

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


if __name__ == "__main__":
    # start = time.time()
    execute()
    # print("--- %s seconds ---" % (time.time() - start))
