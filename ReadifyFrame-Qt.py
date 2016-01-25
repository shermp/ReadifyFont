from __future__ import absolute_import, division, print_function, unicode_literals
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, \
    QLineEdit, QCheckBox, QComboBox, QRadioButton, QSlider, QLabel, QPushButton, QFileDialog, QTextEdit
from PyQt5.QtCore import Qt, QProcess
from FontInfo import FontInfo
import os
import sys
import helper

SEL_REGULAR = 1
SEL_ITALIC = 2
SEL_BOLD = 3
SEL_BOLDITALIC = 4
SEL_NONE = 0

class RF_Qt(QMainWindow):
    def __init__(self):
        super(RF_Qt, self).__init__()
        self.fnt_styles = ['Regular', 'Italic', 'Bold', 'Bold Italic']
        self.fnt_sty_combo_list = []
        self.fnt_file_name_list = []
        self.font_files = None
        self.font_info = FontInfo()
        self.cli_process = QProcess(self)
        self.cli_process.setProcessChannelMode(QProcess.MergedChannels)
        self.cli_process.readyRead.connect(self.dataReady)
        win_layout = QVBoxLayout()
        gb_fnt_files = QGroupBox('Font Files')
        gb_fnt_files.setStyleSheet('QGroupBox { font-weight: bold; }')
        grid_f_f = QGridLayout()
        grid_pos = 0

        # Font Files and styles #
        for i in range(len(self.fnt_styles)):
            self.fnt_file_name_list.append(QLabel('Load font file...'))
            cmb = QComboBox()
            cmb.addItem('')
            cmb.addItems(self.fnt_styles)
            cmb.setEnabled(False)
            self.fnt_sty_combo_list.append(cmb)
            row, col = helper.calc_grid_pos(grid_pos, 2)
            grid_f_f.addWidget(self.fnt_file_name_list[i], row, col)
            grid_pos += 1
            row, col = helper.calc_grid_pos(grid_pos, 2)
            grid_f_f.addWidget(self.fnt_sty_combo_list[i], row, col)
            grid_pos += 1
        grid_f_f.setColumnStretch(0, 1)
        gb_fnt_files.setLayout(grid_f_f)
        win_layout.addWidget(gb_fnt_files)

        # New Font Name #
        gb_fnt_name = QGroupBox('Font Family Name')
        gb_fnt_name.setStyleSheet('QGroupBox { font-weight: bold; }')
        hb_fnt_name = QHBoxLayout()
        self.new_fnt_name = QLineEdit()
        self.new_fnt_name.setToolTip('Enter a name for the modified font.')
        self.new_fnt_name.textEdited[str].connect(self.set_family_name)
        hb_fnt_name.addWidget(self.new_fnt_name)
        gb_fnt_name.setLayout(hb_fnt_name)
        win_layout.addWidget(gb_fnt_name)

        # Options #
        hb_options = QHBoxLayout()

        ## Kerning, Panose, Alt. Name ##
        gb_basic_opt = QGroupBox('Basic Options')
        gb_basic_opt.setStyleSheet('QGroupBox { font-weight: bold; }')
        hb_basic_opt = QHBoxLayout()
        self.basic_opt_list = []
        basic_tooltips = ('<qt/>Some readers and software require \'legacy\', or \'old style\' kerning to be '
                                      'present for kerning to work.',
                          '<qt/>Kobo readers can get confused by PANOSE settings. This option sets all '
                                        'PANOSE information to 0, or \'any\'',
                          '<qt/>Some fonts have issues with renaming. If the generated font does not have '
                                        'the same internal font name as you entered, try enabling this option.')

        for opt, tip in zip(('Legacy Kerning', 'Clear PANOSE', 'Alt. Name'), basic_tooltips):
            self.basic_opt_list.append(QCheckBox(opt))
            self.basic_opt_list[-1].setToolTip(tip)
            hb_basic_opt.addWidget(self.basic_opt_list[-1])

        gb_basic_opt.setLayout(hb_basic_opt)
        hb_options.addWidget(gb_basic_opt)

        ## Hinting ##
        gb_hint_opt = QGroupBox('Hinting Option')
        gb_hint_opt.setStyleSheet('QGroupBox { font-weight: bold; }')
        hb_hint_opt = QHBoxLayout()
        self.hint_opt_list = []
        for opt in ('Keep Existing', 'Remove Existing', 'AutoHint'):
            self.hint_opt_list.append(QRadioButton(opt))
            self.hint_opt_list[-1].toggled.connect(self.set_hint)
            hb_hint_opt.addWidget(self.hint_opt_list[-1])

        self.hint_opt_list[0].setChecked(Qt.Checked)
        gb_hint_opt.setLayout(hb_hint_opt)
        hb_options.addWidget(gb_hint_opt)

        win_layout.addLayout(hb_options)

        ## Darken ##
        gb_dark_opt = QGroupBox('Darken Options')
        gb_dark_opt.setStyleSheet('QGroupBox { font-weight: bold; }')
        hb_dark_opt = QHBoxLayout()
        self.darken_opt = QCheckBox('Darken Font')
        self.darken_opt.setToolTip('<qt/>Darken, or add weight to a font to make it easier to read on e-ink screens.')
        self.darken_opt.toggled.connect(self.set_darken_opt)
        hb_dark_opt.addWidget(self.darken_opt)
        self.mod_bearing_opt = QCheckBox('Modify Bearings')
        self.mod_bearing_opt.setToolTip('<qt/>By default, adding weight to a font increases glyph width. Enable this '
                                        'option to set the glyph width to be roughly equal to the original.<br/><br/>'
                                        'WARNING: This reduces the spacing between glyphs, and should not be used if')
        self.mod_bearing_opt.toggled.connect(self.set_mod_bearing)
        self.mod_bearing_opt.setEnabled(False)
        hb_dark_opt.addWidget(self.mod_bearing_opt)

        self.lbl = QLabel('Darken Amount:')
        self.lbl.setEnabled(False)
        hb_dark_opt.addWidget(self.lbl)
        self.darken_amount_opt = QSlider(Qt.Horizontal)
        self.darken_amount_opt.setMinimum(1)
        self.darken_amount_opt.setMaximum(50)
        self.darken_amount_opt.setValue(12)
        self.darken_amount_opt.setEnabled(False)
        self.darken_amount_opt.valueChanged[int].connect(self.set_darken_amount)
        hb_dark_opt.addWidget(self.darken_amount_opt)
        self.darken_amount_lab = QLabel()
        self.darken_amount_lab.setText(str(self.darken_amount_opt.value()))
        self.darken_amount_lab.setEnabled(False)
        hb_dark_opt.addWidget(self.darken_amount_lab)
        gb_dark_opt.setLayout(hb_dark_opt)

        win_layout.addWidget(gb_dark_opt)

        # Buttons #
        hb_buttons = QHBoxLayout()
        hb_buttons.addStretch()
        self.gen_ttf_btn = QPushButton('Generate TTF')
        self.gen_ttf_btn.clicked.connect(self.gen_ttf)
        hb_buttons.addWidget(self.gen_ttf_btn)
        self.load_font_btn = QPushButton('Load Fonts')
        self.load_font_btn.clicked.connect(self.load_fonts)
        hb_buttons.addWidget(self.load_font_btn)
        hb_buttons.addStretch()
        win_layout.addLayout(hb_buttons)

        gb_log_win = QGroupBox('Log Window')
        gb_log_win.setStyleSheet('QGroupBox { font-weight: bold; }')
        vb_log = QVBoxLayout()
        self.log_win = QTextEdit()
        self.log_win.setAcceptRichText(False)
        vb_log.addWidget(self.log_win)
        gb_log_win.setLayout(vb_log)
        win_layout.addWidget(gb_log_win)

        # Show Window #
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(win_layout)
        self.setWindowTitle('Readify Font')

        self.show()

    def set_basic_opt(self):
        opt = self.sender()
        if opt.isChecked():
            if 'kerning' in opt.text().lower():
                self.font_info.leg_kern = True
            if 'panose' in opt.text().lower():
                self.font_info.strip_panose = True
            if 'alt' in opt.text().lower():
                self.font_info.name_hack = True
        else:
            if 'kerning' in opt.text().lower():
                self.font_info.leg_kern = False
            if 'panose' in opt.text().lower():
                self.font_info.strip_panose = False
            if 'alt' in opt.text().lower():
                self.font_info.name_hack = False

    def set_family_name(self, name):
        self.font_info.font_name = name

    def set_darken_amount(self, amount):
        self.darken_amount_lab.setText(str(amount))
        self.font_info.add_weight = amount

    def set_hint(self):
        hint = self.sender()
        if hint.isChecked():
            if 'keep' in hint.text().lower():
                self.font_info.change_hint = 'keep'
            elif 'remove' in hint.text().lower():
                self.font_info.change_hint = 'remove'
            elif 'auto' in hint.text().lower():
                self.font_info.change_hint = 'auto'

    def set_darken_opt(self):
        if self.sender().isChecked():
            self.mod_bearing_opt.setEnabled(True)
            self.lbl.setEnabled(True)
            self.darken_amount_lab.setEnabled(True)
            self.darken_amount_opt.setEnabled(True)
            self.set_darken_amount(self.darken_amount_opt.value())
        else:
            self.mod_bearing_opt.setEnabled(False)
            self.lbl.setEnabled(False)
            self.darken_amount_lab.setEnabled(False)
            self.darken_amount_opt.setEnabled(False)
            self.set_darken_amount(0)

    def set_mod_bearing(self):
        if self.mod_bearing_opt.isChecked():
            self.font_info.mod_bearings = True
        else:
            self.font_info.mod_bearings = False

    def load_fonts(self):
        f_f = QFileDialog.getOpenFileNames(self, 'Load Fonts', '', 'Font Files (*.ttf, *.otf)')
        self.font_files = f_f[0]
        f_f_names = []
        for file in self.font_files:
            file = os.path.normpath(file)
            base, fn = os.path.split(file)
            f_f_names.append(fn)

        for f_file, f_label, f_style in zip(f_f_names, self.fnt_file_name_list, self.fnt_sty_combo_list):
            f_label.setText(f_file)
            f_style.setEnabled(True)
            if 'regular' in f_file.lower():
                f_style.setCurrentIndex(SEL_REGULAR)
            elif 'bold' in f_file.lower() and 'italic' in f_file.lower():
                f_style.setCurrentIndex(SEL_BOLDITALIC)
            elif 'bold' in f_file.lower():
                f_style.setCurrentIndex(SEL_BOLD)
            elif 'italic' in f_file.lower():
                f_style.setCurrentIndex(SEL_ITALIC)

    # The following method was adapted from: http://stackoverflow.com/a/22110924
    def dataReady(self):
        output = str(self.cli_process.readAllStandardOutput(), encoding=sys.getdefaultencoding())
        self.log_win.append(output)

    def enable_ttf(self):
        pass

    def gen_ttf(self):
        if not self.font_info.out_dir:
            save_dir = os.path.normpath(QFileDialog.getExistingDirectory(self, 'Select save directory...'))
            if save_dir:
                self.font_info.out_dir = save_dir
        else:
            save_dir = os.path.normpath(QFileDialog.getExistingDirectory(self, 'Select Save directory...',
                                                                         self.font_info.out_dir))
            if save_dir:
                self.font_info.out_dir = save_dir

        for file, style in zip(self.font_files, self.fnt_sty_combo_list):
            if style.currentIndex() == SEL_REGULAR:
                self.font_info.font_file_reg = file
            elif style.currentIndex() == SEL_BOLDITALIC:
                self.font_info.font_file_bi = file
            elif style.currentIndex() == SEL_BOLD:
                self.font_info.font_file_bd = file
            elif style.currentIndex() == SEL_ITALIC:
                self.font_info.font_file_it = file

        cli_opt_list = self.font_info.gen_cli_command()
        print(cli_opt_list)
        self.cli_process.start('fontforge', cli_opt_list)

def main():
    app = QApplication(sys.argv)
    rf = RF_Qt()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
