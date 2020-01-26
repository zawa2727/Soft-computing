import numpy as np
import random

class Maze():
    """ 迷路を作るクラス"""
    PATH = 0
    WALL = 1

    def __init__(self, width, height):
        self.maze = []
        self.width = width
        self.height = height
        # 迷路は、幅高さ5以上の奇数で生成する。
        if(self.height < 5 or self.width < 5):
            print('at least 5')
            exit()
        if (self.width % 2) == 0:
            self.width += 1
        if (self.height % 2) == 0:
            self.height += 1

    def set_out_wall(self):
        """ 迷路全体を構成する2次元配列、迷路の外周を壁とし、それ以外を通路とする。"""
        for _x in range(0, self.width):
            row = []
            for _y in range(0, self.height):
                if (_x == 0 or _y == 0 or _x == self.width-1 or _y == self.height -1):
                    cell = self.WALL
                else:
                    cell = self.PATH
                row.append(cell)
            self.maze.append(row)
        return self.maze

    def set_inner_wall_boutaosi(self):
        """迷路の中に棒を立ててランダムな方向に倒す。
        外周の内側に基準となる棒を1セルおき、(x, y ともに偶数の座標)に配置する。"""
        for _x in range(2, self.width-1, 2):
            for _y in range(2, self.height-1, 2):
                self.maze[_x][_y] = self.WALL
                # 棒をランダムな方向に倒して壁とする。
                # (ただし以下に当てはまる方向以外に倒す。)
                # 1行目の内側の壁以外では上方向に倒してはいけない。
                # すでに棒が倒され壁になっている場合、その方向には倒してはいけない。
                while True:
                    if _y == 2:
                        direction = random.randrange(0, 4)
                    else:
                        direction = random.randrange(0, 3)
                    # 棒を倒して壁にする方向を決める。
                    wall_x = _x
                    wall_y = _y
                    # 右
                    if direction == 0:
                        wall_x += 1
                    # 下
                    elif direction == 1:
                        wall_y += 1
                    # 左
                    elif direction == 2:
                        wall_x -= 1
                    # 上
                    else:
                        wall_y -= 1
                    # 壁にする方向が壁でない場合は壁にする。
                    if self.maze[wall_x][wall_y] != self.WALL:
                        self.maze[wall_x][wall_y] = self.WALL
                        break
        return self.maze

    def set_start_goal(self):
        """ スタートとゴールを迷路にいれる。"""
        self.maze[1][1] = 'S'
        self.maze[self.width-2][self.height-2] = 'G'
        return self.maze

    def get_maze(self,maze_list):
        """ 迷路を出力する。"""
       
        for row in self.maze:
            list = []
            for cell in row:
                if cell == self.PATH:
                    list.append(1)
                    #print('1', end='')
                elif cell == self.WALL:
                    list.append(0)
                    #print('0', end='')
                elif cell == 'S':
                    list.append('S')
                    #print('S', end='')
                elif cell == 'G':
                    list.append('G')
                    #print('G', end='')
            maze_list.append(list)
maze_list = []
maze_len = 10#【重要】迷路の長さ(20x20以上にする場合は、遺伝子の長さに3倍ほど余裕を持たせると成功率が上がる。)
newline_check = maze_len+1
maze = Maze(maze_len, maze_len)
maze.set_out_wall()
maze.set_inner_wall_boutaosi()
maze.set_start_goal()
maze.get_maze(maze_list)

print("↓↓↓　　今回のお題【迷路】　　↓↓↓")
cnt = 1
for buff1 in maze_list:
    for buff2 in buff1:
        if(buff2 == 0):
            print('#####' ,end="")
        elif(buff2 == 1):
            print('     ',end="")
        elif(buff2 == 'S'):
            print("START", end="")
        else:
            print("GOAL!",end="")
        if(cnt % newline_check ==0):
            print()
        cnt += 1



"""GA START"""
generation_length = 10000           #【重要】世代の数
seed_num = 20                       #【重要】1世代ごとの個体
genom_length = (maze_len-2) * 2     #【重要】遺伝子の長さ(10x10では最短16、20x20では最短26...NxNでは最短(N-2)*2)だが、歩数に余裕を持たせると成功率が上がる。
seeds = {} #個体格納用のリスト
direction = {0 : [-1, 0], 1 : [0, 1], 2 : [1, 0], 3 : [0, -1]} #上(0)下(2)左(3)右(1)
mutant_ratio = 0.01 #突然変異率
generation = 0 #世代管理
top_second = [] #上位2位の個体用のリスト
score = []#スコア格納用のリスト
#penalty = 2 #ペナルティの重み

def init_seed():#遺伝子初期化
    for i in range(seed_num):
        seeds[i] = []
        for j in range(genom_length):
            seeds[i].append(random.randint(0,3))#ランダムに0-3(上下左右)のパラメータを持つ遺伝子を生成
        
def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]

def scoring(seed):#各遺伝子のスコア計算
    start = [1,1]
    goal = [maze_len-1,maze_len-1]
    position = start
    for i in range(genom_length):#遺伝子の順番に移動できるかを判定
        if maze_list[position[0]+direction[seed[i]][0]][position[1]+direction[seed[i]][1]] == 0:#移動先が壁の場合
            continue
        else:#移動先が通路の場合
            position[0] = position[0] + direction[seed[i]][0]
            position[1] = position[1] + direction[seed[i]][1]
    score.append((goal[0]-position[0]) + (goal[1] - position[1]))#壁を無視したゴールまでの距離をスコアとする。(局所解から抜け出しにくい)

    """ 到達地点からゴールまでの壁の数を計算し、その分だけペナルティを課した結果をスコアとする。  
    x_wall,y_wall = 0,0
    #x_penalty,y_penalty = 0,0
    
    for x in range(position[0],maze_len):
        if maze_list[x][position[1]] == 0:x_wall += 1 
        for y in range(position[1],maze_len):
            if maze_list[position[0]][y] == 0:y_wall += 1
    wall = x_wall + y_wall
    xy_penalty = penalty * wall
    score.append(((goal[0]-position[0]) + (goal[1] - position[1])) * xy_penalty)
    """
 
def get_top_second(score):#選択(今回は最も優秀な２つを選択する)
    top2=[]
    top2_num = []
    top2 = sorted(score)[:2]
    top2_num.append(score.index(top2[0]))
    top2_num.append(score.index(top2[1]))
    return top2_num

def crossing_genom(seed1, seed2):#交叉
    new_genom1 = []
    new_genom2 = []
    a = random.randint(0, genom_length)
    b = random.randint(a, genom_length)
    new_genom1 = seed1[:a] + seed2[a:b] + seed1[b:]
    new_genom2 = seed2[:a] + seed1[a:b] + seed2[b:]
    return new_genom1, new_genom2

def mutant():#突然変異
    for i in range(0,seed_num):
        for j in range(genom_length):
            m = random.random()
            if m <= mutant_ratio:
                new_direction = random.randint(0,3)
                while new_direction == seeds[i][j]:
                    new_direction = random.randint(0,3)
                seeds[i][j] = new_direction
            else:
                continue

def make_seed(top2):#次の世代の個体を生成する
    global generation
    new_seed = {}
    """遺伝子の数を10で固定する場合、以下の処理
    new_seed[0] = seeds[top2[0]]#前世代の1位
    new_seed[1] = seeds[top2[1]]#前世代の2位
    m1 = crossing_genom(seeds[top_second[0]], seeds[top_second[1]])
    new_seed[2] = m1[0]#1位と2位の交叉
    new_seed[3] = m1[1]#1位と2位の交叉
    m2 = crossing_genom(seeds[top_second[0]], seeds[top_second[1]])
    new_seed[4] = m2[0]#1位と2位の交叉
    new_seed[5] = m2[1]#1位と2位の交叉
    m3 = crossing_genom(seeds[top_second[0]], seeds[top_second[1]])
    new_seed[6] = m3[0]#1位と2位の交叉
    new_seed[7] = m3[1]#1位と2位の交叉
    new_seed[8] = [random.randint(0,3) for i in range(genom_length)]#ランダム個体
    new_seed[9] = [random.randint(0,3) for i in range(genom_length)]#ランダム個体    
    """
    #遺伝子の数を増やす場合、以下の処理(交叉個体の選出はランダムになる)
    for i in range(seed_num):
        if i < 2:
            #TOP2
            new_seed[i] = seeds[top2[i]]
        elif (i/seed_num)*100 <= 80:
            #seedの数が80%以内であれば交叉個体を選出
            cross = crossing_genom(seeds[top_second[0]], seeds[top_second[1]])
            new_seed[i] = cross[int(random.random())]
        else:
            #残りの20%はランダム個体とする(多様性を持たせる)
            new_seed[i] = [random.randint(0,3) for i in range(genom_length)]#ランダム個体
    seeds.clear()#前世代の遺伝子をクリアする
    for i in range(seed_num):
        seeds[i] = []
        seeds[i] = new_seed[i]

def next_generation():#世代をすすめる
    global generation
    generation += 1

#遺伝子作成→世代数を上限に選択・交叉・突然変異を繰り返す(main)
init_seed()
while generation < generation_length:
    target = 0
    #while(1):
    for i in range(seed_num):
        scoring(seeds[i])
    if target in score:break
    top_second = get_top_second(score)
    if generation == generation_length - 1:
        next_generation()
    else:
        make_seed(top_second)
        mutant()
        next_generation()
        score.clear()

#操作終了、結果を出力
cnt=1
for buff1 in maze_list:
    for buff2 in buff1:
        print(buff2 ,end="")
        if(cnt % newline_check ==0):
            print()
        cnt += 1
print("LAST_SCORE:",end="")
print(score)
for key,val in seeds.items():
    print(key+1,end="")
    print(":",end="")
    print(val)
print("*OPERATION CHECK* 上(0)下(2)左(3)右(1)")
if(generation < generation_length):#指定した世代以内に処理が終了している場合(ゴールが見つかっている)
    ans = score.index(target)
    print("%d代目の第%d個体がゴールへの経路を発見！" %(generation,ans+1))
else:#最終世代までループした場合(ゴールは見つかっていない)
    ans = score.index(min(score))
    print("近似解:%d代目の第%d個体" %(generation,ans+1))
answer = []
answer = seeds[ans]
start = [1,1]
goal = [maze_len-1,maze_len-1]
position = start
for i in range(len(answer)):
        if maze_list[position[0]+direction[answer[i]][0]][position[1]+direction[answer[i]][1]] == 0 or maze_list[position[0]+direction[answer[i]][0]][position[1]+direction[answer[i]][1]] == 'S' or maze_list[position[0]+direction[answer[i]][0]][position[1]+direction[answer[i]][1]] == 'G':
            continue
        else:
            maze_list[position[0]+direction[answer[i]][0]][position[1]+direction[answer[i]][1]] = "/////"
            position[0] = position[0] + direction[answer[i]][0]
            position[1] = position[1] + direction[answer[i]][1]
cnt = 1
for buff1 in maze_list:
    for buff2 in buff1:
        if(buff2 == 0):
            print('#####' ,end="")
        elif(buff2 == 1):
            print('     ',end="")
        elif(buff2 == 'S'):
            print("START", end="")
        elif(buff2 == 'G'):
            print("GOAL!",end="")
        else:
            print(buff2,end="")
        if(cnt % newline_check ==0):
            print()
        cnt += 1
