import random
import tkinter
import copy
from heapq import *
import time

'''Definirea clasei Node cu parametrii:

  parent - nodul parinte care contine configuratia precedenta de la care s-a ajuns la configuratia actuala
  path - succesiunea de noduri de la nodul intial la nodul curent
  heuristic - euristica folosita pentru calculul scorului nodului
  x - linia pe care se afla celula apasata pentru a ajunge la configuratia actuala
  y - coloana ...

'''

class Node:
    def __init__(self, parent, path, heuristic, game, moves, x, y):
        self.parent = parent
        self.path = path
        if parent is not None:
            self.path.append(parent)
        self.heuristic = heuristic
        self.game = game
        self.moves = moves
        self.x = x
        self.y = y

    def is_final_good(self):      #verifica daca nodul curent este un nod scop
        return self.game.discovered_squares == self.game.number_of_squares - self.game.number_of_bombs

    def is_final_bad(self):     # verifica daca nodul curent contine o configuratie in care a fost apasata o celula cu mina
        return self.game.bombed is True

    def is_final(self):
        return self.is_final_good() or self.is_final_bad()

    def cost(self):
        if self.heuristic == 1:  #miscarea optima descopera cat mai multe casute
           return self.game.number_of_squares - self.game.discovered_squares
        if self.heuristic == -1:
            return  self.game.discovered_squares



'''
  Obiectele din clasa Minesweeper reprezinta configuratii ale tablei de joc. Parametrii sunt:

  n - numarul de linii
  m - numarul de coloane
  number_of_bombs - numarul de mine de pe tabla
  discovered_squares - numarul de celule deja descoperite
  bombed - statutul tablei in functie daca a fost apasata o mina sau nu
  table - matricea de valori a tablei unde -1 reprezinta o mina iar restul valorilor reprezinta numarul de mine vecine
  cover - matrice care retine ce celule au fost descoperite deja, 0 pentru acoperite si 1 pentru descoperite
  chance -
  remaining_bombs - numarul de mine care nu au fost inca localizate

'''
class Minesweeper:

    def __init__(self, n, m, number_of_bombs, discovered_squares, bombed, table, cover):
        self.n = n
        self.m = m
        self.number_of_bombs = number_of_bombs
        self.number_of_squares = n * m
        self.discovered_squares = discovered_squares
        self.bombed = bombed
        self.table = table
        self.cover = cover

    def print_cover(self):
        for row in self.cover:
            print(row)

    def print_table(self):
        for row in self.table:
            print(row)

    def opened_cell(self, x, y): #metoda prin care o celula este descoperita
        opened_cells = [(x,y)]
        self.cover[x][y] = 1 #celula descoperita
        self.discovered_squares += 1
        if self.table[x][y] == -1:
            self.bombed = True
            return []

        l1 = max(0, x - 1)
        l2 = min(self.n - 1, x + 1)
        c1 = max(0, y - 1)
        c2 = min(self.m - 1, y + 1)


        if self.table[x][y] == 0: #celule fara mine in vecinatate deschid celule din jurul lor
            for i in range(l1, l2 + 1):
                for j in range(c1, c2 + 1):
                    if self.cover[i][j] == 0:
                        opened_cells = opened_cells + self.opened_cell(i, j)
        return opened_cells

    def closed_cell(self, x, y): # (pentru bidirectional search) acopera celule
       closed_cells = [(x,y)]
       self.cover[x][y] = 0
       self.discovered_squares -= 1
       if self.table[x][y] == -1:
          self.bombed = True
          return []
       l1 = max(0, x - 1)
       l2 = min(self.n - 1, x + 1)
       c1 = max(0, y - 1)
       c2 = min(self.m - 1, y + 1)


       if self.table[x][y] == 0: #celule fara bombe inchid celule din jurul lor
            for i in range(l1, l2 + 1):
                for j in range(c1, c2 + 1):
                    if self.cover[i][j] == 1:
                        closed_cells = closed_cells + self.closed_cell(i, j)
       return closed_cells


def generate_game(n, m, number_of_bombs):
    table = [[0 for j in range(m)] for i in range(n)]
    cover_start = [[0 for j in range(m)] for i in range(n)]
    cover_stop = [[1 for j in range(m)] for i in range(n)]
    for bomb in range(number_of_bombs):
        x = random.randint(0, n - 1)
        y = random.randint(0, m - 1)
        while table[x][y] == -1:
            x = random.randint(0, n - 1)
            y = random.randint(0, m - 1)
        cover_stop[x][y] = 0
        table[x][y] = -1
    for x in range(n):
        for y in range(m):
            if table[x][y] == -1:
                l1 = max([0, x - 1])
                l2 = min([n - 1, x + 1])
                c1 = max([0, y - 1])
                c2 = min([m - 1, y + 1])
                for a in range(l1, l2 + 1):
                   for b in range(c1, c2 + 1):
                     if table[a][b] != -1:
                        table[a][b] += 1
    start_game = Minesweeper(n, m, number_of_bombs, 0, False, table, cover_start)
    stop_game = Minesweeper(n, m, number_of_bombs, n * m - number_of_bombs, False, table, cover_stop)
    return start_game, stop_game

def get_key(dict, keys, value):
    for key in keys:
        if dict[key] == value:
            return key
    return None

def a_star(start_node):
    win_paths = []
    open_set = []
    heappush(open_set, (start_node.cost(), start_node.game.cover)) #este utilizata o structura heap pentru a retine nodurile din setul open
    visited_config = {start_node : start_node.game.cover}
    closed_set = []
    start = time.time()
    #start_node.game.print_cover()
    while len(open_set) > 0:
        keys = list(visited_config.keys())
        currentNode = get_key(visited_config, keys, heappop(open_set)[1]) #procesarea nodului cu cel mai bun scor din setul open
        closed_set.append(currentNode.game.cover)
        n = currentNode.game.n
        m = currentNode.game.m
        x = 0
        already_opened = []
        open_set = []
        for i in range(n):
            for j in range(m):

                if currentNode.game.cover[i][j] == 0 and (i,j) not in already_opened: #sunt adaugate in heap nodurile ce pot fi create prin miscari pe tabla actuala
                    newNode = copy.deepcopy(currentNode)
                    newNode.parent = currentNode
                    newNode.path.append(currentNode)
                    newNode.moves = currentNode.moves + 1
                    newNode.x = i
                    newNode.y = j
                    opened_cells = newNode.game.opened_cell(i, j)
                    already_opened = already_opened + opened_cells
                    if newNode.is_final_bad():
                        continue

                    if newNode.is_final_good():
                        return newNode




                    keys = list(visited_config.keys())
                    values = list(visited_config.values())
                    key = get_key(visited_config, keys, newNode.game.cover)
                    if newNode.game.cover in values and newNode.cost() >= key.cost():  #se verifica daca configuratia la care s-a ajuns a mai fost vizitata inainte si a obtinut un scor mai bun
                        continue
                    else:
                        if key is not None:
                            key.parent = newNode.parent
                            key.moves = newNode.moves
                    if newNode.is_final_bad() is False and newNode.game.cover not in closed_set:
                        heappush(open_set, (newNode.cost(), newNode.game.cover))
                        x += 1
                        visited_config.update({newNode: newNode.game.cover})

                       # if currentNode.parent != None and currentNode.parent.cost() == currentNode.cost() + 1:
                        #  newNode.path += [currentNode for x in range(currentNode.cost())]
                         # return newNode




        #currentNode.game.print_cover()
        print(currentNode.cost())
       # if time.time() - start > 10:
        #  return currentNode
    return None


game1 = generate_game(16, 16, 40)[0]
#game2 = generate_game(16, 16, 40)
#game3 = generate_game(30, 16, 99)
node = Node(None, [], 1, game1, 0, None, None)
node.game.print_table()
start = time.time()
win = a_star(node)
end = time.time()

print("The time of execution  is :",
      (end-start) * 10**3, "ms")

i = 1
for node in win.path:
    print("Nodul ", i, node)
    i = i + 1
    node.game.print_cover()
    print('\n')
print("Nodul ", i)
win.game.print_cover()


import tkinter as tk



p = win.path
p.append(win)
print(p)
n = win.game.n
m = win.game.m
table = win.game.table
root = tk.Tk()
root.title("Minesweeper")
canvas = tk.Canvas(root, width= m * 30, height= n * 30)
canvas.pack()

print(n, m)



def show_board():
    global p
    if len(p) == 0:
        return
    cover = p[0].game.cover
    p = p[1:]

    for x in range(n):
        for y in range(m):
            if cover[x][y] == 0:
                canvas.create_rectangle(x * 30, y * 30, (x + 1) * 30, (y + 1) * 30, fill='grey')
                canvas.create_text((x + 0.5) * 30, (y + 0.5) * 30, text='', fill='grey')
            else:
                if table[x][y] == -1:
                    canvas.create_rectangle(x * 30, y * 30, (x + 1) * 30, (y + 1) * 30, fill='red')
                    canvas.create_text((x + 0.5) * 30, (y + 0.5) * 30, text='B', fill='black')
                else:
                    canvas.create_rectangle(x * 30, y * 30, (x + 1) * 30, (y + 1) * 30, fill='white')
                    if table[x][y] == 0:
                        canvas.create_text((x + 0.5) * 30, (y + 0.5) * 30, text=' ', fill='black')
                    else:
                        canvas.create_text((x + 0.5) * 30, (y + 0.5) * 30, text=str(table[x][y]), fill='black')
    root.after(1000, show_board)

show_board()
root.mainloop()
