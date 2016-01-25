# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

def iterDic(dic, pythonTwo):
    """
    Return a python 2/3 compatible iterable
    :param dic:
    :param pythonTwo:
    :return:
    """
    if pythonTwo:
        return dic.viewitems()
    else:
        return dic.items()

def calc_grid_pos(pos, cols):
    """
    A little function to calculate the grid position of checkboxes
    :param pos:
    :param cols:
    :return:
    """
    calc_row = pos // cols
    calc_col = pos % cols

    return calc_row, calc_col