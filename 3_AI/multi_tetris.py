import tkinter as tk
from tkinter import messagebox
import random


from util import *

cell_size = 30
C = 36
R = 20
height = R * cell_size
width = C * cell_size

GENSPEED = 4
FPS = 20  # 刷新页面的毫秒间隔
range_length = 7

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
        height = r * cell_size
        width = c * cell_size
        super().__init__(master, width=width, height=height)
        self.pack()

    def init(self):
        for ri in range(self.r):
            for ci in range(self.c):
                self.draw_cell_by_cr(ci, ri, '')

    def draw_cell_by_cr(self, c, r, color, kind=None):
        x0 = c * cell_size
        y0 = r * cell_size
        x1 = c * cell_size + cell_size
        y1 = r * cell_size + cell_size
        # 三种类型
        # 没有俄罗斯方块，None
        # 失效的俄罗斯方块，dead
        # 俄罗斯方块，kind 代表第几个
        if kind is None:
            self.create_rectangle(x0, y0, x1, y1, fill="#CCCCCC", outline="white", width=2)
        elif kind == "dead":
            _tag = 'r%s' % r
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tags=_tag)
        else:
            _tag = 'b%s' % kind
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tags=_tag)

    def draw_block(self, block, kind):
        c, r = block['cr']
        shape_type = block['kind']
        cell_list = block['cell_list']
        for cell in cell_list:
            cell_c, cell_r = cell
            ci = cell_c + c
            ri = cell_r + r
            # 判断该位置方格在画板内部(画板外部的方格不再绘制)
            if 0 <= c < C and 0 <= r < R:
                self.draw_cell_by_cr(ci, ri, SHAPESCOLOR[shape_type], kind)

    def clean_by_block_id(self, block_id):
        _tag = 'b%s' % block_id
        self.delete(_tag)

    def clean_by_row(self,r):
        _tag = 'r%s' % r
        self.delete(_tag)


class GameApp:
    def __init__(self, c, r):
        self.win = tk.Tk()

        height = r * cell_size
        width = c * cell_size

        self.win.geometry("%sx%s+%s+%s" % (width, height, 200, 200))

        self.fps = 50
        self.future_board = []
        self.board = []
        self.block_list = {}
        self.block_id = 0
        self.running = True

        self.c = c
        self.r = r

        self.score = 0
        self.win.title("SCORES: %s" % self.score)
        self.drawer = Drawer(self.win, c, r, cell_size)
        self.drawer.init()
        self.init_board()
        self.count = 0

    def init_board(self):
        self.board=[
            ['' for ci in range(self.c)] for ri in range(self.r)
        ]
        self.future_board=[
            ['' for ci in range(self.c)] for ri in range(self.r)
        ]

    def check_and_clear(self):
        has_complete_row = False
        for ri in range(self.r):
            if check_row_complete(self.board[ri]):
                has_complete_row = True
                # 当前行可消除
                if ri > 0:
                    for cur_ri in range(ri, 0, -1):
                        self.board[cur_ri] = self.board[cur_ri-1][:]
                    self.board[0] = ['' for j in range(C)]
                else:
                    self.board[ri] = ['' for j in range(C)]

                self.score += 10

        if has_complete_row:
            for r in range(self.r):
                self.drawer.clean_by_row(r)
                for c in range(self.c):
                    v = self.board[r][c]
                    if v:
                        self.drawer.draw_cell_by_cr(c, r, SHAPESCOLOR[v], 'dead')

            self.win.title("SCORES: %s" % self.score)

    def game_loop(self):
        if self.running:
            self.win.update()

            if self.count % GENSPEED == 0:
                self.generate_new_block()

            self.move_block_list()
            self.check_and_clear()

            self.count += 1

            self.win.after(self.fps, self.game_loop)

    def run(self):
        self.game_loop()
        self.win.mainloop()

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
        ci = random.randint(0, self.c - 1)
        cr = [self.c // 2, 0]
        cr = [ci, 0]

        new_block = {
            'kind': kind,  # 对应俄罗斯方块的类型
            'cell_list': SHAPES[kind],
            'cr': cr
        }

        if self.block_id ==0:
            new_block = {
                'kind': 'Z',  # 对应俄罗斯方块的类型
                'cell_list': SHAPES['S'],
                'cr': cr
            }
        elif self.block_id ==1:
            new_block = {
                'kind': 'I',  # 对应俄罗斯方块的类型
                'cell_list': SHAPES['I'],
                'cr': cr
            }

        # 使用未来的board 进行计算，
        self.calculate_best_place(new_block)
        # 计算完了再把最终位置存到未来的board
        save_block_to_list(new_block, self.future_board, True)
        check_and_clear(self.future_board)

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

    def get_bottom_r(self, cell_list, ci):
        for ri in range(R-1, -1, -1):
            if self.check_move((ci, ri), cell_list, (0, 0)):
                for dc in [0, 1, -1]:
                    nci = ci + dc
                    if self.check_move((nci, ri), cell_list, (0, 0)) and \
                            self.check_above_empty(cell_list, nci, ri):
                        return ri, dc

        raise Exception("no space to place")

    def check_col_accessible(self, c, cell_list):
        for cell in cell_list:
            cell_c, cell_r = cell
            ci = cell_c + c
            if ci < 0 or ci > self.c-1:
                return False

        return True

    def calculate_best_place(self, block):
        shape_type = block['kind']

        block_c,block_r = block['cr']
        index_id = {}
        index_score = {}
        index = 0
        for angle in range(4):
            cell_list = get_cell_list_by_angle(SHAPES[shape_type], angle)
            left, right = get_range(block_c, self.c, range_length)
            for ci in range(self.c):
                if self.check_col_accessible(ci, cell_list):
                    index += 1
                    ri, dc = get_bottom_r(cell_list, self.future_board, ci)
                    # ri, dc = self.get_bottom_r(cell_list, ci)

                    cur_board = [row[:] for row in self.future_board]
                    end_block = {
                        'kind': shape_type,
                        'cell_list': cell_list,
                        'cr': (ci, ri)
                    }
                    save_block_to_list(end_block, cur_board)
                    index_id[index] = {
                        'cr': (ci, ri),
                        'dc': dc,
                        'angle': angle
                    }
                    index_score[index] = cal_ai_score(cur_board, self.c, self.r)

        key_name = max(index_score, key=index_score.get)

        best_c = index_id[key_name]['cr'][0]
        if abs(best_c-block_c)>range_length:
            left, right = get_range(best_c, self.c, range_length)
            change_c = random.randint(left, right)
            block['cr'] = (change_c, block_r)
        block['best'] = index_id[key_name]

        cal_move_order(block)


game = GameApp(C, R)
game.run()