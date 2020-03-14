import numpy as np
from random import seed
from random import randint
import time
import threading
import os
seed(time.time())


def randPair(s, e):
    return np.random.randint(s, e), np.random.randint(s, e)


class BoardPiece:

    def __init__(self, name, code, pos):
        self.name = name  # name of the piece
        self.code = code  # an ASCII character to display on the board
        self.pos = pos  # 2-tuple e.g. (1,4)
        self.score = 0


class GridBoard:

    def __init__(self, size=4):
        self.size = size  # Board dimensions, e.g. 4 x 4
        self.components = {}  # name : board piece

    def addPiece(self, name, code, pos=(0, 0)):
        newPiece = BoardPiece(name, code, pos)
        self.components[name] = newPiece

    def movePiece(self, name, pos):
        self.components[name].pos = pos

    def delPiece(self, name):
        del self.components[name]

    def render(self):
        dtype = '<U2'
        displ_board = np.zeros((self.size, self.size), dtype=dtype)
        displ_board[:] = ' '

        for name, piece in self.components.items():
            displ_board[piece.pos] = piece.code
        return displ_board

    def render_np(self):
        num_pieces = len(self.components)
        displ_board = np.zeros((num_pieces, self.size, self.size), dtype=np.uint8)
        layer = 0
        for name, piece in self.components.items():
            pos = (layer,) + piece.pos
            displ_board[pos] = 1
            layer += 1
        return displ_board


def addTuple(a, b):
    return tuple([sum(x) for x in zip(a, b)])


class Gridworld:

    def __init__(self, size, food):
        self.score = 0
        self.food = food
        if size >= 4:
            self.board = GridBoard(size=size)
        else:
            print("Minimum board size is 4. Initialized to size 4.")
            self.board = GridBoard(size=4)

        # Add pieces, positions will be updated later
        self.board.addPiece('Player', 'P', (0, 0))
        for i in range(self.food):
            self.board.addPiece('Food' + str(i), '+', (1, 0))
        self.board.addPiece('Ghost', 'G', (2, 0))
        self.iniGird(food)

    def validateBoard(self):
        all_positions = [piece.pos for name, piece in self.board.components.items()]
        if len(all_positions) > len(set(all_positions)):
            return False
        else:
            return True

    def iniGird(self, food):
        temp = []
        num = 0
        self.board.components['Player'].pos = (0, 0)
        temp.append((0, 0))

        loc = randPair(0, self.board.size)

        if (loc[0] % 2 == 0):

            pair = (0, np.random.randint(1, self.board.size))
            self.board.components['Ghost'].pos = pair
            temp.append(pair)
        else:
            pair = (np.random.randint(1, self.board.size), 0)
            self.board.components['Ghost'].pos = pair
            temp.append(pair)

        while food:
            loc = randPair(0, self.board.size)
            if (loc not in temp):
                self.board.components['Food' + str(num)].pos = loc
                temp.append(loc)
                food -= 1
                num += 1

    def makeMove(self, action, obj):
        # need to determine what object (if any) is in the new grid spot the player is moving to
        # actions in {u,d,l,r}
        if obj == 'Player':
            def checkMove(addpos=(0, 0)):

                new_pos = addTuple(self.board.components['Player'].pos, addpos)
                if max(new_pos) > (self.board.size - 1):  # if outside bounds of board
                    self.score -= 10
                    print("Dead")
                    return False
                elif min(new_pos) < 0:  # if outside bounds
                    self.score -= 10
                    print("Dead")
                    return False
                else:
                    for j in list(self.board.components):

                        if self.board.components[j].pos == new_pos and j != 'Player':
                            self.board.delPiece(j)
                            self.food -= 1
                    self.board.movePiece('Player', new_pos)
                    self.score += 5
                    if self.food == 0:
                        temp = []
                        num = 0
                        temp.append(self.board.components['Player'].pos)
                        temp.append(self.board.components['Ghost'].pos)

                        print('updating food')
                        update_food = randint(1, (self.board.size * self.board.size) - 2)
                        self.food = update_food
                        while update_food:
                            loc = randPair(0, self.board.size)
                            if (loc not in temp):
                                self.board.addPiece('Food' + str(num), '+', loc)
                                temp.append(loc)
                                update_food -= 1
                                num += 1
                return True

            if action == 'u':  # up
                if not checkMove((-1, 0)):
                    print(self.score)
                    return False

            elif action == 'd':  # down
                if not checkMove((1, 0)):
                    print(self.score)
                    return False
            elif action == 'l':  # left
                if not checkMove((0, -1)):
                    print(self.score)
                    return False
            elif action == 'r':  # right
                if not checkMove((0, 1)):
                    print(self.score)
                    return False
            else:
                return True
                pass

        else:
            if action == 'u':
                new_pos = addTuple(self.board.components['Ghost'].pos, (-1, 0))
                if (new_pos[0] == -1):
                    self.board.movePiece('Ghost', (self.board.size - 1, new_pos[1]))
                elif (new_pos[1] == -1):
                    self.board.movePiece('Ghost', (new_pos[0], self.board.size - 1))
                else:
                    self.board.movePiece('Ghost', (new_pos[0] % self.board.size, new_pos[1] % self.board.size))


            elif action == 'd':
                new_pos = addTuple(self.board.components['Ghost'].pos, (1, 0))
                if (new_pos[0] == -1):
                    self.board.movePiece('Ghost', (self.board.size - 1, new_pos[1]))
                elif (new_pos[1] == -1):
                    self.board.movePiece('Ghost', (new_pos[0], self.board.size - 1))
                else:
                    self.board.movePiece('Ghost', (new_pos[0] % self.board.size, new_pos[1] % self.board.size))

            elif action == 'l':
                new_pos = addTuple(self.board.components['Ghost'].pos, (0, -1))
                if (new_pos[0] == -1):
                    self.board.movePiece('Ghost', (self.board.size - 1, new_pos[1]))
                elif (new_pos[1] == -1):
                    self.board.movePiece('Ghost', (new_pos[0], self.board.size - 1))
                else:
                    self.board.movePiece('Ghost', (new_pos[0] % self.board.size, new_pos[1] % self.board.size))

            elif action == 'r':
                new_pos = addTuple(self.board.components['Ghost'].pos, (0, 1))
                if (new_pos[0] == -1):
                    self.board.movePiece('Ghost', (self.board.size - 1, new_pos[1]))
                elif (new_pos[1] == -1):
                    self.board.movePiece('Ghost', (new_pos[0], self.board.size - 1))
                else:
                    self.board.movePiece('Ghost', (new_pos[0] % self.board.size, new_pos[1] % self.board.size))

    def dispGrid(self):
        #         print(self.board.components['Player'].pos)
        return self.board.render()

def ghostmove(game):
    move=['u','d','l','r']
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        game.makeMove(move[randint(0,3)],'Ghost')
        pprint(game.dispGrid())
        time.sleep(10)
def pprint(A):
    if A.ndim==1:
        print(A)
    else:
        w = max([len(str(s)) for s in A])
        print(u'\u250c'+u'\u2500'*w+u'\u2510')
        for AA in A:
            print(' ', end='')
            print('[', end='')
            for i,AAA in enumerate(AA[:-1]):
                w1=max([len(str(s)) for s in A[:,i]])
                print(str(AAA)+' '*(w1-len(str(AAA))+1),end='')
            w1=max([len(str(s)) for s in A[:,-1]])
            print(str(AA[-1])+' '*(w1-len(str(AA[-1]))),end='')
            print(']')
        print(u'\u2514'+u'\u2500'*w+u'\u2518')



game=Gridworld(size=5,food=2)
pprint(game.dispGrid())

x = threading.Thread(target=ghostmove, args=(game,))
x.start()

while True:
    temp=input()
    print(game.makeMove(temp,'Player'))

    print('Game Over')
    print("score is :",game.score)
x.join()
exit(0)