# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE! -- Ummmm... Oops?
###########################################################################

from __future__ import unicode_literals
import wx
import wx.xrc

###########################################################################
## Class ReadifyFrame
###########################################################################

class ReadifyFrame ( wx.Frame ):
    
    def __init__( self, parent ):
        """
        Create a new frame with various controls for selecting fonts and options.
        :param parent:
        :return:
        """
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Readify Font", pos = wx.DefaultPosition, \
                            size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        parentCont = wx.BoxSizer( wx.VERTICAL )
        
        # Font Chooser #
        contFont = wx.BoxSizer( wx.HORIZONTAL )
        
        contFonts = wx.BoxSizer( wx.VERTICAL )

        listContFontLayout = []
        
        self.listTxtFont = []
        self.listChoiceStyle = []
        chceStyleChoices = [ "Regular", "Italic", "Bold", "Bold Italic", wx.EmptyString ]

        for i in range(0,4):
            listContFontLayout.append( wx.BoxSizer( wx.HORIZONTAL ) )
            self.listTxtFont.append(wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 ))
            listContFontLayout[i].Add( self.listTxtFont[i], 1, wx.ALL, 5 )
            self.listChoiceStyle.append(wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, chceStyleChoices, 0 ))
            self.listChoiceStyle[i].SetSelection( 4 )
            self.listChoiceStyle[i].SetToolTipString("Set the font style")
            listContFontLayout[i].Add( self.listChoiceStyle[i], 0, wx.ALL, 5 )

            contFonts.Add( listContFontLayout[i], 1, wx.EXPAND, 5 )
        
        contFont.Add( contFonts, 1, wx.EXPAND, 5 )
        
        self.btnChooseFont = wx.Button( self, wx.ID_ANY, "Browse Fonts...", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.btnChooseFont.SetToolTipString("Choose one or more fonts to modify.")
        contFont.Add( self.btnChooseFont, 0, wx.ALL, 5 )
                
        parentCont.Add( contFont, 0, wx.EXPAND|wx.TOP, 5 )
        

        # Font Name #
        contFontName = wx.BoxSizer( wx.HORIZONTAL )
        
        self.lblFontFamName = wx.StaticText( self, wx.ID_ANY, "Font Family Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lblFontFamName.Wrap( -1 )
        self.lblFontFamName.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
        
        contFontName.Add( self.lblFontFamName, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        self.txtFontFamName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        self.txtFontFamName.SetToolTipString("Enter a name for the modified font.")
        contFontName.Add( self.txtFontFamName, 1, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )
        
        parentCont.Add( contFontName, 0, wx.EXPAND, 5 )

        # Options #
        contOptions = wx.BoxSizer( wx.HORIZONTAL )
        """
        self.chkHint = wx.CheckBox( self, wx.ID_ANY, u"Remove Hinting", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chkHint.SetToolTipString("Strip hinting information from the generated TrueType font")
        contOptions.Add( self.chkHint, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        """
        self.chkKern = wx.CheckBox( self, wx.ID_ANY, "Legacy Kerning", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chkKern.SetToolTipString("Some readers and software require 'legacy', or 'old style' kerning to be "
                                      "present for kerning to work.")
        contOptions.Add( self.chkKern, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.chkPANOSE = wx.CheckBox( self, wx.ID_ANY, "Remove PANOSE", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chkPANOSE.SetToolTipString("Kobo readers can get confused by PANOSE settings. This option sets all "
                                        "PANOSE information to 0, or 'any'")
        contOptions.Add( self.chkPANOSE, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.chkAltName = wx.CheckBox( self, wx.ID_ANY, "Alt. Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chkAltName.SetToolTipString("Some fonts have issues with renaming. If the generated font does not have "
                                         "the same internal font name as you entered, try enabling this option.")
        contOptions.Add( self.chkAltName, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        rboxHintsChoices = [ "Keep Existing", "Remove Existing", "Autohint" ]
        self.rboxHints = wx.RadioBox( self, wx.ID_ANY, u"Hints", wx.DefaultPosition, wx.DefaultSize, rboxHintsChoices, 1, wx.RA_SPECIFY_ROWS )
        self.rboxHints.SetSelection( 0 )
        contOptions.Add( self.rboxHints, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        parentCont.Add( contOptions, 0, wx.EXPAND, 5 )

        # Darken Settings #
        contDarkenFont = wx.BoxSizer( wx.HORIZONTAL )
        
        self.lblDarkenAmount = wx.StaticText( self, wx.ID_ANY, "Darken Font Amount", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lblDarkenAmount.Wrap( -1 )
        self.lblDarkenAmount.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
        
        contDarkenFont.Add( self.lblDarkenAmount, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )
        
        self.txtDarkenAmount = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        self.txtDarkenAmount.SetToolTipString("Enter a number between 1 and 100 to add weight to the font. 50 is "
                                              "considered bold"
                                              "\n10-15 seems to work well to make fonts a bit darker.")
        contDarkenFont.Add( self.txtDarkenAmount, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )
        
        self.chkBearing = wx.CheckBox( self, wx.ID_ANY, "Adjust Bearing", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.chkBearing.SetToolTipString("By default, adding weight to a font increases glyph width. Enable this "
                                         "option to set the glyph width to be roughly equal to the original.\n"
                                         "WARNING: This reduces the spacing between glyphs, and should not be used if "
                                         "you have added too much weight.")
        contDarkenFont.Add( self.chkBearing, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )

        parentCont.Add( contDarkenFont, 0, wx.EXPAND, 5 )

        # Output Directory Picker #
        contOut = wx.BoxSizer( wx.HORIZONTAL )

        self.lblOutDir = wx.StaticText( self, wx.ID_ANY, "Output Directory", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lblOutDir.Wrap( -1 )
        self.lblOutDir.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
        contOut.Add( self.lblOutDir, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )
        
        self.pickerOutDir = wx.DirPickerCtrl( self, wx.ID_ANY, "", "Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
        self.pickerOutDir.SetToolTipString("Choose the output directory to save the modified font files in.")
        contOut.Add( self.pickerOutDir, 1, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )

        parentCont.Add( contOut, 0, wx.EXPAND, 5 )

        # Preview Font
        contPreviewFont = wx.BoxSizer( wx.HORIZONTAL )

        self.lblPreviewFont = wx.StaticText( self, wx.ID_ANY, "Preview Text", wx.DefaultPosition, wx.DefaultSize,
                                          0 )
        self.lblPreviewFont.Wrap( -1 )
        self.lblPreviewFont.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
        contPreviewFont.Add( self.lblPreviewFont, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )

        self.txtPreview = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        contPreviewFont.Add( self.txtPreview, 1, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5 )

        self.btnPrevFont = wx.Button( self, wx.ID_ANY, "Preview Font", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.btnPrevFont.SetToolTipString("Preview the changes using a small subset of the font.")
        contPreviewFont.Add( self.btnPrevFont, 0, wx.ALL, 5 )

        parentCont.Add( contPreviewFont, 0, wx.EXPAND, 5 )

        # Log Output #
        contOutput = wx.BoxSizer( wx.VERTICAL )

        self.lblOutputLog = wx.StaticText( self, wx.ID_ANY, "Output Log", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
        self.lblOutputLog.Wrap( -1 )
        self.lblOutputLog.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
        
        contOutput.Add( self.lblOutputLog, 0, wx.ALL, 5 )
        self.txtOutput = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_DONTWRAP|wx.TE_MULTILINE|wx.TE_READONLY )
        self.txtOutput.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 76, 90, 90, False, wx.EmptyString ) )
        #self.txtOutput.Enable( False )

        contOutput.Add( self.txtOutput, 1, wx.ALL|wx.EXPAND, 5 )
        
        parentCont.Add( contOutput, 1, wx.EXPAND, 5 )

        # Buttons #
        contGenerate = wx.BoxSizer( wx.HORIZONTAL )

        self.btnGenTTF = wx.Button( self, wx.ID_ANY, "Generate TTF", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.btnGenTTF.SetToolTipString("Generates a new set of font files using the information entered above.")
        contGenerate.Add( self.btnGenTTF, 0, wx.ALL, 5 )


        self.btnClear = wx.Button( self, wx.ID_ANY, "Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.btnClear.SetToolTipString("Clear all fields in the form.")
        contGenerate.Add( self.btnClear, 0, wx.ALL, 5 )

        parentCont.Add( contGenerate, 0, wx.CENTER|wx.BOTTOM, 5 )

        self.SetSizer( parentCont )
        self.Layout()
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.btnChooseFont.Bind( wx.EVT_BUTTON, self.chooseFiles )
        self.btnGenTTF.Bind( wx.EVT_BUTTON, self.genTTF )
        self.btnPrevFont.Bind(wx.EVT_BUTTON, self.previewFont )
        self.btnClear.Bind( wx.EVT_BUTTON, self.clearForm )
    
    def __del__( self ):
        pass

    # Virtual event handlers, overide them in your derived class
    def chooseFiles( self, event ):
        event.Skip()
    
    def genTTF( self, event ):
        event.Skip()

    def previewFont(self, event ):
        event.Skip()
    
    def clearForm( self, event ):
        event.Skip()
