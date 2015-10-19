from ReadifyFrame import *
import os
import subprocess
import sys

MISSING_VALUE = 1
INVALID_VALUE = 2
PROC_OS_ERROR = 100
PROC_SUCCESS = 0

SEL_REGULAR = 0
SEL_ITALIC = 1
SEL_BOLD = 2
SEL_BOLDITALIC = 3
SEL_NONE = 4

class ReadifyFontGUI(ReadifyFrame):
    """
    This class extends the ReadifyFrame class. It shows the GUI described in the parent class, and handles the events to
    choose fonts, and generate new font files.
    """
    fontDir = None
    def __init__(self):
        super(ReadifyFontGUI, self).__init__(None)
        ReadifyFontGUI.Show(self)

    def chooseFiles(self, event):
        """
        Browse for font files using default file dialog box. Font files are added to the wxTextCtrl,
        and the subfamily of font is automatically determined if possible.
        :param event:
        :return:
        """
        dialog = wx.FileDialog(self, "Choose a file", "", "", "*.otf", wx.MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            fileList = dialog.GetFilenames()
            self.fontDir = os.path.dirname(dialog.GetPath())
            # Try to determine font subfamily and set the listChoiceStyle to the appropriate value
            for file, text, style in zip(fileList, self.listTxtFont, self.listChoiceStyle):
                text.SetValue(file)
                if "regular" in file.lower():
                    style.SetSelection(SEL_REGULAR)
                elif "bold" in file.lower() and "italic" in file.lower():
                    style.SetSelection(SEL_BOLDITALIC)
                elif "bold" in file.lower():
                    style.SetSelection(SEL_BOLD)
                elif "italic" in file.lower():
                    style.SetSelection(SEL_ITALIC)
                else:
                    style.SetSelection(SEL_NONE)
            for txtBox in self.listTxtFont:
                if txtBox.GetValue:
                    txtBox.Disable()
                    
    def genTTF(self, event):
        """
        Generate the new font files. Builds a list of command line arguments from the options in the GUI and passes
        the list to the runCLI() function. A status message is displayed, and the output of the runCLI() function is
        displayed in the output text box.
        :param event:
        :return:
        """

        # Create a dictionary of all possible command line arguments, and set all values to None
        optsDic = {"fontname" : None, "regular" : None, "italic" : None, "bold" : None, "bolditalic" : None, "striphint" : None, \
            "legacykern" : None, "outputdir" : None, "addweight" : None, "panosestrip" : None, "modbearings" : None, "namehack" : None}

        # If a font file exits, set its option in the dictionary
        for font, style in zip(self.listTxtFont, self.listChoiceStyle):
            if font.GetValue() and style.GetSelection() == 0:
                optsDic["regular"] = "-r " + os.path.join(self.fontDir, font.GetValue())
            elif font.GetValue() and style.GetSelection() == 1:
                optsDic["italic"] = "-i " + os.path.join(self.fontDir, font.GetValue())
            elif font.GetValue() and style.GetSelection() == 2:
                optsDic["bold"] = "-b " + os.path.join(self.fontDir, font.GetValue())
            elif font.GetValue() and style.GetSelection() == 3:
                optsDic["bolditalic"] = "-B " + os.path.join(self.fontDir, font.GetValue())

        # Set the new font name in the dictionary
        if self.txtFontFamName.GetValue():
            optsDic["fontname"] = self.txtFontFamName.GetValue()

        # Check that a font file and name have been selected by the user
        if not any((optsDic["regular"], optsDic["italic"], optsDic["bold"], optsDic["bolditalic"])):
            wx.MessageBox("You need to choose at least One font")
            return MISSING_VALUE

        if not optsDic["fontname"]:
            wx.MessageBox("You need to choose a new font name!")
            return MISSING_VALUE

        # Add more options to the dictionary
        """
        if self.chkHint.GetValue():
            optsDic["striphint"] = "-s"
        """
        if self.rboxHints.GetSelection() == 0:
            optsDic["changehint"] = "-c keep"
        elif self.rboxHints.GetSelection() == 1:
            optsDic["changehint"] = "-c remove"
        elif self.rboxHints.GetSelection() == 2:
            optsDic["changehint"] = "-c auto"

        if self.chkKern.GetValue():
            optsDic["legacykern"] = "-k"
        if self.chkPANOSE.GetValue():
            optsDic["panosestrip"] = "-p"
        if self.chkAltName.GetValue():
            optsDic["namehack"] = "-n"
        if self.txtDarkenAmount.GetValue():
            # lets check that the user enters a valid number
            try:
                intWeight = int(self.txtDarkenAmount.GetValue())
                if 1 <= intWeight <= 100:
                    optsDic["addweight"] = "-w " + self.txtDarkenAmount.GetValue()
                    if self.chkBearing.GetValue():
                        optsDic["modbearings"] = "-m"
                else:
                    wx.MessageBox("Darken amount too high or low! Please choose a number between 1 and 100 em.")
                    return INVALID_VALUE
            except ValueError:
                wx.MessageBox("You did not enter a valid number! Your font will not be darkened.")
                return INVALID_VALUE

        # Choose an output directory for the generated fonts
        if self.pickerOutDir.GetPath():
            optsDic["outputdir"] = "-d " + self.pickerOutDir.GetPath()
        else:
            optsDic["outputdir"] = "-d " + self.fontDir

        # Create a list of command line arguments to pass to subprocess
        optionsList = ["fontforge", "-script", "ReadifyFontCLI.py"]
        for key, val in optsDic.iteritems():
            if val and key != "fontname":
                optionsList.append(val)
        optionsList.append(optsDic["fontname"])

        # Run script, and obtain its outputs
        cliRetCode, cliOutput = self.runCLI(optionsList)
        strCliOutput = cliOutput.decode(sys.stdout.encoding)
        # Check for success
        if cliRetCode == PROC_OS_ERROR:
            wx.MessageBox("Oops, something went wrong.\nIs FontForge installed and in your PATH?")
        elif cliRetCode != PROC_SUCCESS:
            self.txtOutput.SetValue(strCliOutput)
            wx.MessageBox("The font was not generated. Please see log for details")
        else:
            self.txtOutput.SetValue(strCliOutput)
            wx.MessageBox("The font was successfully generated!")


    def runCLI(self, optList):
        """
        Uses the subprocess.check_output() function to run a list of commands line arguments.
        :param optList:
        :return:
        """
        try:
            rfCLI = subprocess.check_output(optList, stderr=subprocess.STDOUT)

            return PROC_SUCCESS, rfCLI
        # In case fontforge is not in PATH, or some other OS related error
        except OSError:
            return PROC_OS_ERROR, None
        # Check if fontforge script completed successfully or not
        except subprocess.CalledProcessError as scriptFailed:
            retCode = scriptFailed.returncode
            output = scriptFailed.output
            return retCode, output

    def clearForm(self, event):
        """
        Resets/clears all of the elements in the GUI to a clean/new state.
        :param event:
        :return:
        """
        for text, style in zip(self.listTxtFont, self.listChoiceStyle):
            text.SetValue(wx.EmptyString)
            text.Enable()
            style.SetSelection(SEL_NONE)
        self.txtFontFamName.SetValue(wx.EmptyString)
        self.chkAltName.SetValue(False)
        self.chkBearing.SetValue(False)
        #self.chkHint.SetValue(False)
        self.chkKern.SetValue(False)
        self.chkPANOSE.SetValue(False)
        self.rboxHints.SetSelection(0)
        self.pickerOutDir.SetPath(wx.EmptyString)
        self.txtDarkenAmount.SetValue(wx.EmptyString)
        self.txtOutput.SetValue(wx.EmptyString)

if __name__ == "__main__":
    app = wx.App(False)
    frame = ReadifyFontGUI()
    app.MainLoop()
