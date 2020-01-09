#usr/bin/env python
#-*- coding:utf-8- -*-

# 0 不加速
# 1 直接落地
JIASU = 0

def move_block(block, direction):
        c, r = block['cr']
        dc, dr = direction
        block['cr'] = c+dc, r+dr


def get_cell_list_by_angle(cell_list, angle):
    angle_dict = {
        0: (1, 0, 0, 1),
        1: (0, 1, -1, 0),
        2: (-1, 0, 0, -1),
        3: (0, -1, 1, 0),
    }
    a, b, c, d = angle_dict[angle]
    if angle == 0:
        return cell_list

    rotate_cell_list = []
    for cell in cell_list:
        cc, cr = cell
        rc, rr = a * cc + b * cr, c*cc+d*cr
        rotate_cell_list.append((rc, rr))

    return rotate_cell_list


def save_block_to_list(block, board, isFuture = False):
        shape_type = block['kind']
        cc, cr = block['cr']
        cell_list = block['cell_list']

        if isFuture:
            cc, cr = block['best']['cr']
            angle = block['best']['angle']
            cell_list = get_cell_list_by_angle(cell_list,angle)

        for cell in cell_list:
            cell_c, cell_r = cell
            c = cell_c + cc
            r = cell_r + cr
            # block_list 在对应位置记下其类型
            board[r][c] = shape_type


def check_row_complete(row):
    for cell in row:
        if cell=='':
            return False

    return True


def check_move(board, cr, cell_list, direction):
    board_r = len(board)
    board_c = len(board[0])
    cc, cr = cr
    cell_list = cell_list

    for cell in cell_list:
        cell_c, cell_r = cell
        c = cell_c + cc + direction[0]
        r = cell_r + cr + direction[1]
        # 判断该位置是否超出左右边界，以及下边界
        # 一般不判断上边界，因为俄罗斯方块生成的时候，可能有一部分在上边界之上还没有出来
        if c < 0 or c >= board_c or r >= board_r:
            return False

        # 必须要判断r不小于0才行，具体原因你可以不加这个判断，试试会出现什么效果
        if r >= 0 and board[r][c]:
            return False

    return True


def check_above_empty(board, cell_list, ci, ri):
    for cell in cell_list:
        cc, cr = cell
        c, r = ci + cc, ri + cr
        for ir in range(r):
            if board[ir][c]:
                return False

    return True


def get_bottom_r(cell_list, board, ci):
    board_r = len(board)
    for ri in range(board_r-1, -1, -1):
        if check_move(board, (ci, ri), cell_list, (0, 0)):
            for dc in [0, 1, -1]:
                nci = ci + dc
                if check_move(board, (nci, ri), cell_list, (0, 0)) and \
                        check_above_empty(board, cell_list, nci, ri):
                    return ri, dc

    raise Exception("no space to place")


def cal_ai_score(blist, board_c, board_r):
    aggregate_height = 0
    holes = 0
    row_hight_list = []
    for ci in range(board_c):
        find_first_cell = False
        for ri in range(board_r):
            if not find_first_cell and blist[ri][ci]:
                h = board_r - ri
                aggregate_height += h*h
                row_hight_list.append(h)
                find_first_cell = True
            elif find_first_cell and not blist[ri][ci]:
                holes += 1

        if not find_first_cell:
            row_hight_list.append(0)

    complete_lines = 0
    for row in blist:
        if check_row_complete(row):
            complete_lines += 1

    bumpiness = 0
    for ci in range(board_c - 1):
        bumpiness += abs(row_hight_list[ci] - row_hight_list[ci+1])
    a = -2.10066
    b = 2.760666
    c = -0.35663
    d = -0.184483

    p = a * aggregate_height + b * complete_lines + c*holes + d*bumpiness
    return p


def cal_move_order(block):
    # 计算出移动到最佳位置的路径
    cc, cr = block['cr']
    best = block['best']
    bc, br = best['cr']
    dc = best['dc']
    bdc = bc + dc
    angle_change_count = best['angle']  # 需要旋转的次数
    horizontal_move_count = abs(bdc - cc)  # 需要水平移动的次数

    speed = (angle_change_count + horizontal_move_count + 1) // br + 1  # 每下落一次移动次数

    steps = ['' for _ in range(br+1)]

    for si in range(br):
        if angle_change_count >= speed:
            steps[si] = 'W'*speed
            angle_change_count -= speed
        else:
            step = 'W'*angle_change_count
            for i in range(speed - angle_change_count):
                if bdc < cc:
                    step += 'A'
                    cc -= 1
                elif bdc > cc:
                    step += 'D'
                    cc += 1
                else:
                    break

            angle_change_count = 0
            steps[si] = step

    if dc == 0:
        steps[br] = ''
    elif dc == 1:
        steps[br] = 'A'
    elif dc == -1:
        steps[br] = 'D'

    block['move_steps'] = steps


def move_block_by_step(block):
    step_count = len(block['move_steps'])
    si = block['cur_step']
    if si >= step_count:
        return False

    step_str = block['move_steps'][si]
    c, r = block['cr']
    cell_list = block['cell_list']

    if step_str == '' and JIASU == 1:
        if all(block['move_steps'][next_si] == '' for next_si in range(si,step_count)):
            si = step_count
            r = step_count - 1
            block['cur_step'] = si
            block['cr'] = (c, r)
            return True

    for step in step_str:
        if step == 'A':
            c -= 1
        elif step == 'D':
            c += 1
        elif step == 'W':
            cell_list = get_cell_list_by_angle(cell_list, 1)

    if si == step_count - 1:
        pass
    else:
        r += 1
        # return False

    si += 1
    block['cur_step'] = si
    block['cr'] = (c, r)
    block['cell_list'] = cell_list
    return True


def check_and_clear(board):
    score = 0
    board_r = len(board)
    board_c = len(board[0])
    for ri in range(board_r):
        if check_row_complete(board[ri]):
            # 当前行可消除
            if ri > 0:
                for cur_ri in range(ri, 0, -1):
                    board[cur_ri] = board[cur_ri-1][:]
                board[0] = ['' for j in range(board_c)]
            else:
                board[ri] = ['' for j in range(board_c)]

            score += 10

    return score


def get_range(block_c, board_c, length):
    if block_c < length:
        return 0, min(board_c, 2*length)
    elif block_c > board_c - length:
        return max(0, board_c - 2*length), board_c
    else:
        return block_c-length, block_c +length