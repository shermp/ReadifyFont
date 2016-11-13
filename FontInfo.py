from __future__ import absolute_import, division, print_function, unicode_literals
import os

class FontInfo():
    """
    Create an object to store various font modification options, and generate a list of command line options to be be
    passed into the CLI script
    """
    def __init__(self):
        self.font_name = ''
        self.font_file_reg = ''
        self.font_file_it = ''
        self.font_file_bd = ''
        self.font_file_bi = ''
        self.change_hint = ''
        self.leg_kern = False
        self.strip_panose = False
        self.name_hack = False
        self.extract_sc = False
        self.add_weight = 0
        self.mod_bearings = False
        self.out_dir = ''

    def gen_cli_command(self):
        """
        Generate all options for the CLI script.
        :return:
        """
        cli_command = ['-script', 'ReadifyFontCLI.py']
        if self.font_file_reg:
            cli_command.append('-r')
            cli_command.append(os.path.normpath(self.font_file_reg))
        if self.font_file_it:
            cli_command.append('-i')
            cli_command.append(os.path.normpath(self.font_file_it))
        if self.font_file_bd:
            cli_command.append('-b')
            cli_command.append(os.path.normpath(self.font_file_bd))
        if self.font_file_bi:
            cli_command.append('-B')
            cli_command.append(os.path.normpath(self.font_file_bi))

        if self.leg_kern:
            cli_command.append('-k')
        if self.strip_panose:
            cli_command.append('-p')
        if self.name_hack:
            cli_command.append('-n')
        if self.extract_sc:
            cli_command.append('-s')

        if self.change_hint in ('keep', 'remove', 'auto'):
            cli_command.append('-c')
            cli_command.append(self.change_hint)

        if 0 < self.add_weight <= 50:
            cli_command.append('-w')
            cli_command.append(str(self.add_weight))
            if self.mod_bearings:
                cli_command.append('-m')

        if self.out_dir:
            cli_command.append('-d')
            cli_command.append(os.path.normpath(self.out_dir))

        cli_command.append(self.font_name)

        return cli_command

    def clear(self):
        self.font_name = ''
        self.font_file_reg = ''
        self.font_file_it = ''
        self.font_file_bd = ''
        self.font_file_bi = ''
        self.change_hint = ''
        self.leg_kern = False
        self.strip_panose = False
        self.name_hack = False
        self.extract_sc = False
        self.add_weight = 0
        self.mod_bearings = False
        self.out_dir = ''