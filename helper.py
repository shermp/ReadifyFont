# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
import os, sys

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

def valid_filename(name):
    """
    A basic check for invalid characters in filenames.
    :param name:
    :return:
    """
    invalid_char = '\/:*?"<>|'
    if any(char in name for char in invalid_char):
        return False
    else:
        return True
'''
NOTE: The following function has been copied from https://hg.python.org/cpython/file/default/Lib/shutil.py

I am including it here because it is not included in python versions < 3.3.
'''
def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.

    """
    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, mode):
        return (os.path.exists(fn) and os.access(fn, mode)
                and not os.path.isdir(fn))

    # If we're given a path with a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    if os.path.dirname(cmd):
        if _access_check(cmd, mode):
            return cmd
        return None

    if path is None:
        path = os.environ.get("PATH", os.defpath)
    if not path:
        return None
    path = path.split(os.pathsep)

    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if not os.curdir in path:
            path.insert(0, os.curdir)

        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See if the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        # If it does match, only test that one, otherwise we have to try
        # others.
        if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
            files = [cmd]
        else:
            files = [cmd + ext for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    for dir in path:
        normdir = os.path.normcase(dir)
        if not normdir in seen:
            seen.add(normdir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                if _access_check(name, mode):
                    return name
    return None