"""
block字典结构:
{
    "kind": kind,
    "cell_list": SHAPES[kind],
    "cr": [c,r],
    best: {'cr': (ci, ri),'dc': dc,'angle': angle}
    'move_steps': [step0,step1,...](step0为列表对象存储字符串,如‘ADW’),     Example:'move_steps': ['WWA', 'AAA', 'A', '']
    'cur_step': 0(cur_step描述move_steps偏移量,如move_steps[cur_step] == ‘WWA’)
}

board列表结构:
board[ri][ci] = ''
"""

import tkinter as tk
import random

from util import *

cell_size = 30
C = 12
R = 20
height = R * cell_size
width = C * cell_size

FPS = 20  # 刷新页面的毫秒间隔

# 定义各种形状
SHAPES = {
    "O": [(-1, -1), (0, -1), (-1, 0), (0, 0)],
    "S": [(-1, 0), (0, 0), (0, -1), (1, -1)],
    "T": [(-1, 0), (0, 0), (0, -1), (1, 0)],
    "I": [(0, 1), (0, 0), (0, -1), (0, -2)],
    "L": [(-1, 0), (0, 0), (-1, -1), (-1, -2)],
    "J": [(-1, 0), (0, 0), (0, -1), (0, -2)],
    "Z": [(-1, -1), (0, -1), (0, 0), (1, 0)],
}

# 定义各种形状的颜色
SHAPESCOLOR = {
    "O": "#d25b6a",
    "S": "#d2835b",
    "T": "#e5e234",
    "I": "#83d05d",
    "L": "#2862d2",
    "J": "#35b1c0",
    "Z": "#5835c0"
}


class Drawer(tk.Canvas):
    def __init__(self, master, c, r, cell_size):
        self.c = c
        self.r = r
        self.cell_size = cell_size
        height = R * cell_size
        width = C * cell_size
        super().__init__(master, width=width, height=height)
        self.pack()

    # 初始化（也可以用来重置），用默认色填充画板
    def init(self):
        for ri in range(self.r):
            for ci in range(self.c):
                self.draw_cell_by_cr(ci, ri, '')

    # 对指定位置的格子进行涂色(通过坐标及tag_kind，tag_kind决定tags)
    def draw_cell_by_cr(self, c, r, color, tag_kind=None):
        x0 = c * cell_size
        y0 = r * cell_size
        x1 = c * cell_size + cell_size
        y1 = r * cell_size + cell_size
        # 三种类型
        # 没有俄罗斯方块，None
        # 失效的俄罗斯方块，dead(已落地，不能移动的俄罗斯方块)
        # 俄罗斯方块，kind 代表第几个
        if tag_kind is None:
            self.create_rectangle(x0, y0, x1, y1, fill="#CCCCCC", outline="white", width=2)
        elif tag_kind == "dead":
            _tag = 'r%s' % r
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tags=_tag)
        else:
            _tag = 'b%s' % tag_kind
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tags=_tag)

    # 对指定俄罗斯方块进行涂色，颜色由block[kind]决定，kind由函数参数决定
    def draw_block(self, block, tag_kind):
        c, r = block['cr']
        shape_type = block['kind']
        cell_list = block['cell_list']
        for cell in cell_list:
            cell_c, cell_r = cell
            ci = cell_c + c
            ri = cell_r + r
            # 判断该位置方格在画板内部(画板外部的方格不再绘制)
            if 0 <= c < C and 0 <= r < R:
                self.draw_cell_by_cr(ci, ri, SHAPESCOLOR[shape_type], tag_kind)

    # 按照block_id删除画板上对应对象
    def clean_by_block_id(self, block_id):
        _tag = 'b%s' % block_id
        self.delete(_tag)

    # 按照行坐标r删除画板上对应对象
    def clean_by_row(self, r):
        _tag = 'r%s' % r
        self.delete(_tag)


class GameApp:
    def __init__(self, c, r):
        self.win = tk.Tk()

        self.fps = 50  # 屏幕刷新时间
        self.board = []  # 二维列表，存放面板上的俄罗斯方块类型信息
        self.block_list = {}  # block_list存储所有俄罗斯方块对象，key是id， value是block
        self.block_id = 0  # 对应俄罗斯方块id
        self.running = True

        self.c = c
        self.r = r

        self.score = 0 # 总分数
        self.win.title("SCORES: %s" % self.score)
        self.drawer = Drawer(self.win, c, r, cell_size)
        self.drawer.init()
        self.init_board()

    #  类对象初始化时调用，对类变量board列表初始化
    def init_board(self):
        self.board = [
            ['' for ci in range(self.c)] for ri in range(self.r)
        ]

    #  检查是否有可清理的行，有就清理
    def check_and_clear(self):
        has_complete_row = False
        for ri in range(self.r):
            if check_row_complete(self.board[ri]):
                has_complete_row = True
                # 当前行可消除
                if ri > 0:
                    # 当前行为中间行，清理后，上面的行都下落一行
                    for cur_ri in range(ri, 0, -1):
                        self.board[cur_ri] = self.board[cur_ri-1][:]

                    self.board[0] = ['' for j in range(C)]  # 用新的空行填充首行
                else:
                    self.board[ri] = ['' for j in range(C)]

                self.score += 10  # 清理一行，进行一次加分

        if has_complete_row:
            for r in range(self.r):
                self.drawer.clean_by_row(r)  # 清除一行（遍历完成后会清理所有行
                for c in range(self.c):
                    v = self.board[r][c]
                    if v:
                        self.drawer.draw_cell_by_cr(c, r, SHAPESCOLOR[v], 'dead')

            self.win.title("SCORES: %s" % self.score)  # 更新标题显示的分数

    def game_loop(self):
        if self.running:
            self.win.update()

            if self.block_list:
                self.move_block_list()
                self.check_and_clear()

            else:
                self.generate_new_block()

            self.win.after(self.fps, self.game_loop)

    def run(self):
        self.game_loop()
        self.win.mainloop()

    # 对指定方块能否在指定方向进行移动进行判断，返回值为布尔类型
    def check_move(self, cr, cell_list, direction):
        cc, cr = cr
        cell_list = cell_list

        for cell in cell_list:
            cell_c, cell_r = cell
            c = cell_c + cc + direction[0]
            r = cell_r + cr + direction[1]
            # 判断该位置是否超出左右边界，以及下边界
            # 一般不判断上边界，因为俄罗斯方块生成的时候，可能有一部分在上边界之上还没有出来
            if c < 0 or c >= self.c or r >= self.r:
                return False

            # 必须要判断r不小于0才行，具体原因你可以不加这个判断，试试会出现什么效果
            if r >= 0 and self.board[r][c]:
                return False

        return True

    # 对当前block_list字典中的block进行单步移动
    def move_block_list(self):
        to_del_id = []
        for block_id in self.block_list:
            block = self.block_list[block_id]
            self.drawer.clean_by_block_id(block_id)

            if move_block_by_step(block):
                self.drawer.draw_block(block, block_id)
            else:
                save_block_to_list(block, self.board)
                self.drawer.draw_block(block, 'dead')
                to_del_id.append(block_id)

        for _id in to_del_id:
            del self.block_list[_id]

    def generate_new_block(self):
        kind = random.choice(list(SHAPES.keys()))
        # 对应横纵坐标，以左上角为原点，水平向右为x轴正方向，
        # 竖直向下为y轴正方向，x对应横坐标，y对应纵坐标
        cr = [self.c // 2, 0]
        new_block = {
            'kind': kind,  # 对应俄罗斯方块的类型
            'cell_list': SHAPES[kind],
            'cr': cr
        }
        self.calculate_best_place(new_block)
        new_block['cur_step'] = 0

        self.block_list[self.block_id] = new_block
        self.drawer.draw_block(new_block, self.block_id)

        self.block_id += 1

    def check_above_empty(self, cell_list, ci, ri):
        for cell in cell_list:
            cc, cr = cell
            c, r = ci + cc, ri + cr
            for ir in range(r):
                if self.board[ir][c]:
                    return False

        return True

    # 对指定方块在对应列能满足插入的最下方的行ri进行查找并返回，并返回对应的列偏移量dc
    # dc是为了处理特殊的情况，比如落地后需要左右移动一下的情况
    def get_bottom_r(self, cell_list, ci):
        for ri in range(R-1, -1, -1):
            if self.check_move((ci, ri), cell_list, (0, 0)):
                # 按顺序检查当前位置与右左位置，上方是否没有阻挡，没有则返回
                for dc in [0, 1, -1]:
                    nci = ci + dc
                    if self.check_move((nci, ri), cell_list, (0, 0)) and \
                            self.check_above_empty(cell_list, nci, ri):
                        return ri, dc

        # raise Exception("no space to place")
        return -1, -1

    # 检查俄罗斯方块移动到列c后是否越界，返回值为布尔型，True代表可以移动，False表示不能
    def check_col_accessible(self, c, cell_list):
        for cell in cell_list:
            cell_c, cell_r = cell
            ci = cell_c + c
            if ci < 0 or ci > self.c-1:
                return False

        return True

    # 计算当前最佳位置，进行目标cr，angle,br存储，并调用cal_move_order函数对路径进行存储
    def calculate_best_place(self, block):
        shape_type = block['kind']
        index_id = {}  # 存储俄罗斯方块信息键值对
        index_score = {}  # 存储俄罗斯方块权值键值对
        # 每一种情况都是一个index，
        # 理论上，一个俄罗斯方块落地情况，可分为四个角度，c-1个列， 即共 4(c-1)种情况。
        index = 0
        for angle in range(4):
            cell_list = get_cell_list_by_angle(SHAPES[shape_type], angle)

            for ci in range(C):
                if self.check_col_accessible(ci, cell_list):
                    ri, dc = self.get_bottom_r(cell_list, ci)
                    if ri<0: # 这一列放不了东西
                        continue

                    index += 1

                    # 为每一种场景都复制一个board（深度拷贝），
                    # 使得当前场景的计算不会影响到其他的
                    cur_board = [row[:] for row in self.board]
                    end_block = {
                        'kind': shape_type,
                        'cell_list': cell_list,
                        'cr': (ci, ri)
                    }
                    # 将该情景下的俄罗斯方块存储至新建的board中
                    save_block_to_list(end_block,cur_board)
                    index_id[index] = {
                        'cr': (ci, ri),
                        'dc': dc,
                        'angle': angle
                    }
                    # 计算出当前情况的board权值，并存储到index_score
                    index_score[index] = cal_ai_score(cur_board, self.c, self.r)

        if index == 0: # 没位置可以放，游戏结束
            self.running = False
            return

        try:
            key_name = max(index_score, key=index_score.get)  # 得出最高分数的列表角标

            block['best'] = index_id[key_name]  # 对最佳位置坐标，偏移量，角度flag进行存储
            cal_move_order(block)  # 计算到达最佳位置的路径

            key_name = max(index_score, key=index_score.get)

            block['best'] = index_id[key_name]
            cal_move_order(block)
        except Exception as e:
            self.running = False
            print("game over with e:", e)
            print("score:", self.score)


game = GameApp(C, R)
game.run()