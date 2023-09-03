import copy
import tkinter as tk
import random
import time
from heapq import *


def get_key(dict, keys, value):
    for key in keys:
        if dict[key] == value:
            return key
    return None

class Node:
    def __init__(self, parent, path, heuristic, game, moves, x, y, mistakes = None):
        self.parent = parent
        self.path = path
        if parent is not None:
            self.path.append(parent)
        self.heuristic = heuristic
        self.game = game
        self.moves = moves
        self.x = x
        self.y = y
        self.mistakes = mistakes

    def is_final_good(self):      #verifica daca nodul curent este un nod scop
        return self.game.discovered_squares == self.game.number_of_squares - self.game.number_of_bombs

    def is_final_bad(self):     # verifica daca nodul curent contine o configuratie in care a fost apasata o celula cu mina
        return self.game.bombed is True

    def is_final(self):
        return self.is_final_good() or self.is_final_bad()

    def cost(self):
        if self.heuristic == 1:  #miscarea optima descopera cat mai multe casute
          return self.game.number_of_squares - self.game.discovered_squares
        if self.heuristic == 2 or self.heuristic == 4 :
          return self.game.number_of_squares - len(self.game.flagged) - self.game.discovered_squares
        if self.heuristic == 3:
          return self.game.remaining_bombs

class Minesweeper:

    def __init__(self, n, m, number_of_bombs, discovered_squares, bombed, table, cover, remaining_bombs, flagged, unint):
        self.n = n
        self.m = m
        self.number_of_bombs = number_of_bombs
        self.number_of_squares = n * m
        self.discovered_squares = discovered_squares
        self.bombed = bombed
        self.table = table
        self.cover = cover
        self.remaining_bombs = remaining_bombs
        self.flagged = flagged
        self.unint = unint


    def print_cover(self):
        for row in self.cover:
            print(row)

    def print_table(self):
        for row in self.table:
            print(row)

    def opened_cell(self, x, y): #metoda prin care o celula este descoperita
        opened_cells = [(x,y)]
        self.cover[x][y] = 1 #celula descoperita
        if self.table[x][y] == -1:
            self.bombed = True
            return []

        self.discovered_squares += 1


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

    def undiscovered_neighbours(self, x , y):
        l1 = max(0, x - 1)
        l2 = min(self.n - 1, x + 1)
        c1 = max(0, y - 1)
        c2 = min(self.m - 1, y + 1)
        unk = []
        n_mines = []
        for i in range(l1, l2 + 1):
          for j in range(c1, c2 + 1):
            if i == x and j == y:
              continue
            if self.cover[i][j] == 1:
              continue
            if (i,j) not in self.flagged:
               unk.append((i,j))
            else:
               n_mines.append((i,j))
        return unk, n_mines

    def solve(self):
      global the_path
      to_check = []
      prev_cover = [[0 if self.cover[a][b] == 0 else 1 for b in range(self.m)] for a in range(self.n)]
      for i in range(self.n):
        for j in range(self.m):
          if self.cover[i][j] == 0 or (i,j) in self.unint:
            continue
          unk, n_mines = self.undiscovered_neighbours(i,j)
          if len(unk) == 0:
            self.unint.append((i,j))
          if len(unk) == self.table[i][j] - len(n_mines):
             self.flagged += unk
             unk = []
             self.unint.append((i,j))
          else:
             if self.table[i][j] == len(n_mines):
                 for safe in unk:
                    if self.cover[safe[0]][safe[1]] == 0:
                      self.opened_cell(safe[0], safe[1])
                      cov = [[0 if self.cover[a][b] == 0 else 1 for b in range(self.m)] for a in range(self.n) ]
                      add_flags = [flag for flag in self.flagged]
                      the_path.append((cov, [], add_flags))
             else:
                    to_check += unk
      if prev_cover != [[0 if self.cover[a][b] == 0 else 1 for b in range(self.m)] for a in range(self.n)]:
          to_check = self.solve()
      to_check = [i for i in to_check if i not in self.flagged and self.cover[i[0]][i[1]] == 0]
      return to_check



    def sim_solve(self, a, b):
      self.cover[a][b] = 1
      prev_cover = [[0 if self.cover[a][b] == 0 else 1 for b in range(self.m)] for a in range(self.n)]
      new_flagged = []
      new_saves = []
      for i in range(self.n):
        for j in range(self.m):
          if self.cover[i][j] == 0 or (i,j) in self.unint or (i == a and j == b):
            continue
          unk, n_mines = self.undiscovered_neighbours(i,j)
          if len(unk) == 0:
            continue
          if len(unk) == self.table[i][j] - len(n_mines):
            new_flagged += [z for z in unk if z not in new_flagged]
          else:
             if self.table[i][j] == len(n_mines):
                 for safe in unk:
                    if safe not in new_saves:
                      new_saves.append(safe)
      self.cover[a][b] = 0
      for i in range(self.n):
        for j in range(self.m):
          if self.cover[i][j] == 0 or (i,j) in self.unint:
            continue
          l1 = max(0, i - 1)
          l2 = min(self.n - 1, i + 1)
          c1 = max(0, j - 1)
          c2 = min(self.m - 1, j + 1)
          nb_mines = 0
          '''
          for l in range(l1, l2 + 1):
            for c in range (c1, c2 + 1):
                if (l,c) in new_flagged or (l,c) in self.flagged:
                  nb_mines += 1
          if nb_mines > self.table[i][j]:
            return [-1], [-1]
      '''
      return new_flagged, new_saves



    def calc_weight(self, x, y):
        l1 = max(0, x - 1)
        l2 = min(self.n - 1, y + 1)
        c1 = max(0, x - 1)
        c2 = min(self.m - 1, y + 1)
        w = 0
        for l in range(l1, l2 + 1):
            for c in range(c1, c2 + 1):
                if self.cover[l][c] == 0:
                    continue
                unk, n_mines = self.undiscovered_neighbours(l, c)
                if len(unk) == 0:
                    continue
                chance = (len(unk) - (self.table[l][c] - len(n_mines))) / len(unk)
                if w < chance:
                    w = chance
        return w



def new_a_star_v2(start_node):
  open_set = []
  global the_path
  mistakes = 0
  heappush(open_set, (start_node.cost(), start_node.game.cover))
  visited_config = {start_node : start_node.game.cover}
  closed_set = []
  start = time.time()
  while len(open_set) > 0:
        keys = list(visited_config.keys())
        #print(keys)
        currentNode = get_key(visited_config, keys, heappop(open_set)[1])
        cov = [[0 if currentNode.game.cover[a][b] == 0 else 1 for b in range(currentNode.game.m)] for a in range(currentNode.game.n) ]
        add_flags = [flag for flag in currentNode.game.flagged]
        the_path.append((cov, [], add_flags))
        if currentNode.is_final_bad(): #daca nodul reprezinta o configuratie compromisa, nu mai e extins
          cov = [[0 if currentNode.parent.game.cover[a][b] == 0 else 1 for b in range(currentNode.game.m)] for a in range(currentNode.game.n) ]
          cov = currentNode.parent.game.cover
          currentNode.parent.game.flagged.append((currentNode.x, currentNode.y))
          add_flags = [flag for flag in currentNode.parent.game.flagged]
          the_path.append((cov, [], add_flags))
          for itr in open_set:
            change_node = get_key(visited_config, keys, itr[1])
            change_node.game.flagged.append((currentNode.x, currentNode.y))
          mistakes += 1
          continue
        closed_set.append(currentNode.game.cover)
        n = currentNode.game.n
        m = currentNode.game.m

        #print("No of discoverd squares before")
        #print(currentNode.game.discovered_squares)
        to_check = currentNode.game.solve()

        #print("Cost:")
        #print(currentNode.cost())
        #print("No of discovered square:")
        #print(currentNode.game.discovered_squares)
        add_flags = [flag for flag in currentNode.game.flagged]
        cov = [[0 if currentNode.game.cover[a][b] == 0 else 1 for b in range(currentNode.game.m)] for a in range(currentNode.game.n) ]
        the_path.append((cov, to_check, add_flags))
        if currentNode.game.flagged == currentNode.game.number_of_bombs:
          for i in range(n):
            for j in range(m):
              if currentNode.game.cover[i][j] == 0 and currentNode.game.table[i][j] != -1:
                currentNode.game.opened_cell(i,j)
                add_flags = [flag for flag in currentNode.game.flagged]
                cov = [[0 if currentNode.game.cover[a][b] == 0 else 1 for b in range(currentNode.game.m)] for a in range(currentNode.game.n) ]
                the_path.append((cov, [], add_flags))
        if currentNode.is_final_good():
          return currentNode, mistakes

        #print("A AJUNS AICI")
        #print("Open set", open_set)
        if len(to_check) == 0: #daca nu mai exista celule acoperite si nemarcate, se va crea un nou nod printr-o miscare random pe restul tablei
          print("Cautare oprita, se alege random")
          for x in range(n):
            for y in range(m):
              if (x,y) in currentNode.game.flagged or currentNode.game.cover[x][y] == 1:
                continue
              newNode = copy.deepcopy(currentNode)
              newNode.parent = currentNode
              newNode.path.append(currentNode)
              newNode.moves = currentNode.moves + 1
              newNode.x = x
              newNode.y = y
              opened_cells = newNode.game.opened_cell(x, y)
              if newNode.is_final_bad():   #apasarile de mina sunt inregistrate
               add_flags = [flag for flag in newNode.game.flagged]
               cov = [[0 if newNode.game.cover[a][b] == 0 else 1 for b in range(newNode.game.m)] for a in range(newNode.game.n) ]
               the_path.append((cov, [], add_flags))
               add_flags = [flag for flag in newNode.parent.game.flagged]
               cov = [[0 if newNode.parent.game.cover[a][b] == 0 else 1 for b in range(newNode.game.m)] for a in range(newNode.game.n) ]
               the_path.append((cov, [], add_flags))
               currentNode.game.flagged.append((newNode.x, newNode.y)) #retinem pozitia minei apasate
               currentNode.game.solve()
               continue
              heappush(open_set, (currentNode.cost()  - 1, newNode.game.cover))
              visited_config.update({newNode: newNode.game.cover})
              break


        for cell in to_check: #sunt create noi noduri pe baza celulelor care nu sunt sigure
           #print("Se creeaza noi noduri")
           x = cell[0]
           y = cell[1]
           flags, saves = currentNode.game.sim_solve(x, y)
           #print("New flags:")
           #print(x,y)
           #print(flags)
           if flags == [-1]:
            continue
           newNode = copy.deepcopy(currentNode)
           newNode.parent = currentNode
           newNode.path.append(currentNode)
           newNode.moves = currentNode.moves + 1
           newNode.x = x
           newNode.y = y
           opened_cells = newNode.game.opened_cell(x, y)
           #keys = list(visited_config.keys())
           values = list(visited_config.values())
           if newNode.game.cover in values:
            continue
           #key = get_key(visited_config, keys, newNode.game.cover)
           #print(currentNode.cost())
           if newNode.heuristic == 2:
             heappush(open_set, (currentNode.cost() - len(flags) - len(saves) - 1, newNode.game.cover))
           if newNode.heuristic == 4:
             weight = 1 + currentNode.game.calc_weight(newNode.x, newNode.y)
             heappush(open_set, (currentNode.cost() - weight * (len(flags) - len(saves) - 1), newNode.game.cover))
           visited_config.update({newNode: newNode.game.cover})

        if (time.time() - start) > 1:
            return currentNode, mistakes

def new_generate_game(n, m, number_of_bombs):
    table = [[0 for j in range(m)] for i in range(n)]
    cover = [[0 for j in range(m)] for i in range(n)]
    for bomb in range(number_of_bombs):
        x = random.randint(0, n - 1)
        y = random.randint(0, m - 1)
        while table[x][y] == -1:
            x = random.randint(0, n - 1)
            y = random.randint(0, m - 1)
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
    start_game = Minesweeper(n, m, number_of_bombs, 0, False, table, cover, number_of_bombs, [], [])
    return start_game

#game = new_generate_game(9, 9, 10) # generarea jocului de minesweeper prin tabla initiala
#game = new_generate_game(16, 16, 40)
game = new_generate_game(9, 9, 10)


node = Node(None, [], 4, game, 0, None, None) #crearea nodului radacina
node.game.print_table()
x = random.randint(0, node.game.n - 1) #alegerea celulei de start
y = random.randint(0, node.game.m - 1)
cov = [[0 if node.game.cover[a][b] == 0 else 1 for b in range(node.game.m)] for a in range(node.game.n) ]
print(cov)
the_path = [(cov, [], [])]
while node.game.table[x][y] == -1: #ne asiguram ca celula aleasa in start nu este una cu mina
      x = random.randint(0, node.game.n - 1)
      y = random.randint(0, node.game.m - 1)
start = time.time()
node.game.opened_cell(x,y)
print(cov)
print("PATH", the_path)
win, mistakes = new_a_star_v2(node)
end = time.time()
i = 1
for node in win.path: #reconstituirea drumului parcurs de algoritm
    print("Nodul ", i, node)
    i = i + 1
    node.game.print_cover()
    print('\n')
print("Nodul ", i)
win.game.print_cover()
win.game.print_table()
print(mistakes)
print("The time of execution of above program is :",
      (end-start) * 10**3, "ms")

for cover in the_path:
  for row in cover[0]:
    print(row)
  print('\n')


'''
avg_time = 0
avg_moves = 0
avg_mistakes = 0
count = 0
for i in range(1000):
  print("Configuratia", i)
  the_path = []
  game = new_generate_game(16, 30, 99)
  node = Node(None, [], 2, game, 0, None, None)
  x = random.randint(0, node.game.n - 1)
  y = random.randint(0, node.game.m - 1)
  while node.game.table[x][y] == -1:  # ne asiguram ca celula aleasa in start nu este una cu mina
      x = random.randint(0, node.game.n - 1)
      y = random.randint(0, node.game.m - 1)
  node.game.opened_cell(x, y)
  start = time.time()
  win, mistakes = new_a_star_v2(node)
  end = time.time()
  if win.is_final_good():
    avg_time += (end - start) * 10 ** 3
    avg_moves += len(the_path)
    avg_mistakes += mistakes
    count += 1

print("Average time of execution :", avg_time / count)
print("Average number of moves: ", avg_moves / count)
print("Average number of mistakes: ", avg_mistakes / count)
print("Counted configurations: ", count)
'''
p = the_path
n = node.game.n
m = node.game.m
table = node.game.table
root = tk.Tk()
root.title("Minesweeper")
canvas = tk.Canvas(root, width= m * 30, height= n * 30)
canvas.pack()

print(n, m)


def show_board():
    global p
    if len(p) == 0:
        return
    cover = p[0][0]
    to_check = p[0][1]
    flags = p[0][2]
    p = p[1:]

    for x in range(n):
        for y in range(m):
            if cover[x][y] == 0:
              if (x,y) in flags:
                  canvas.create_rectangle(y * 30, x * 30, (y + 1) * 30, (x + 1) * 30, fill='pink')
                  canvas.create_text((y + 0.5) * 30, (x + 0.5) * 30, text='F', fill='black')
              else:
                if (x,y) in to_check:
                  canvas.create_rectangle(y * 30, x * 30, (y + 1) * 30, (x + 1) * 30, fill='green')
                  canvas.create_text((y + 0.5) * 30, (x + 0.5) * 30, text='', fill='green')
                else:
                    canvas.create_rectangle(y * 30, x * 30, (y + 1) * 30, (x + 1) * 30, fill='grey')
                    canvas.create_text((y + 0.5) * 30, (x + 0.5) * 30, text='', fill='grey')
            else:
              if table[x][y] == -1:
                 canvas.create_rectangle(y * 30, x * 30, (y + 1) * 30, (x + 1) * 30, fill='red')
                 canvas.create_text((y + 0.5) * 30, (x + 0.5) * 30, text='B', fill='black')
              else:
                  canvas.create_rectangle(y * 30, x * 30, (y + 1) * 30, (x + 1) * 30, fill='white')
                  if table[x][y] == 0:
                    canvas.create_text((y + 0.5) * 30, (x + 0.5) * 30, text=' ', fill='black')
                  else:
                    canvas.create_text((y + 0.5) * 30, (x + 0.5) * 30, text=str(table[x][y]), fill='black')
    root.after(1000, show_board)

show_board()
root.mainloop()
