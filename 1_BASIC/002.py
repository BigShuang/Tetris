import tkinter as tk

cell_size = 30
C = 12
R = 20
height = R * cell_size
width = C * cell_size

FPS = 200  # 刷新页面的毫秒间隔

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
    "O": "blue",
    "S": "red",
    "T": "yellow",
    "I": "green",
    "L": "purple",
    "J": "orange",
    "Z": "Cyan",
}


def draw_cell_by_cr(canvas, c, r, color="#CCCCCC"):
    """
    :param canvas: 画板，用于绘制一个方块的Canvas对象
    :param c: 方块所在列
    :param r: 方块所在行
    :param color: 方块颜色，默认为#CCCCCC，轻灰色
    :return:
    """
    x0 = c * cell_size
    y0 = r * cell_size
    x1 = c * cell_size + cell_size
    y1 = r * cell_size + cell_size
    canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2)


# 绘制空白面板
def draw_blank_board(canvas):
    for ri in range(R):
        for ci in range(C):
            draw_cell_by_cr(canvas, ci, ri)


def draw_cells(canvas, c, r, cell_list, color="#CCCCCC"):
    """
    绘制指定形状指定颜色的俄罗斯方块
    :param canvas: 画板
    :param r: 该形状设定的原点所在的行
    :param c: 该形状设定的原点所在的列
    :param cell_list: 该形状各个方格相对自身所处位置
    :param color: 该形状颜色
    :return:
    """
    for cell in cell_list:
        cell_c, cell_r = cell
        ci = cell_c + c
        ri = cell_r + r
        # 判断该位置方格在画板内部(画板外部的方格不再绘制)
        if 0 <= ci < C and 0 <= ri < R:
            draw_cell_by_cr(canvas, ci, ri, color)


win = tk.Tk()
canvas = tk.Canvas(win, width=width, height=height, )
canvas.pack()

draw_blank_board(canvas)


def draw_block_move(canvas, block, direction=[0, 0]):
    """
    绘制向指定方向移动后的俄罗斯方块
    :param canvas: 画板
    :param block: 俄罗斯方块对象
    :param direction: 俄罗斯方块移动方向
    :return:
    """
    shape_type = block['kind']
    c, r = block['cr']
    cell_list = block['cell_list']

    # 移动前，先清除原有位置绘制的俄罗斯方块,也就是用背景色绘制原有的俄罗斯方块
    draw_cells(canvas, c, r, cell_list)

    dc, dr = direction
    new_c, new_r = c+dc, r+dr
    block['cr'] = [new_c, new_r]
    # 在新位置绘制新的俄罗斯方块就好
    draw_cells(canvas, new_c, new_r, cell_list, SHAPESCOLOR[shape_type])


a_block = {
    'kind': 'O',  # 对应俄罗斯方块的类型
    'cell_list': SHAPES['O'],  # 对应俄罗斯方块的各个方格
    'cr': [3, 3]  # 对应横纵坐标，以左上角为原点，水平向右为横坐标轴正方向，竖直向下为纵坐标轴正方向
}

draw_block_move(canvas, a_block)


def game_loop():
    win.update()

    down = [0, 1]
    draw_block_move(canvas, a_block, down)

    win.after(FPS, game_loop)

win.update()
win.after(FPS, game_loop)  # 在FPS 毫秒后调用 game_loop方法


win.mainloop()
