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