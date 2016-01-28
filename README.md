## Readify Font

Readify Font is a python script with an optional wxPython GUI wrapper that modifies fonts for use on common ebook
reading devices. It is derived from an earlier script I made called Koboify Fonts.

Readify Font takes a font with up to four different subfamilies, Applies some tweaks, and generates new TrueType font
 files which can be copied onto an ebook reading device.

Readify Font uses FontForge to perform the font modifications. This is a script/GUI to be able to undertake some
common tasks quickly and easily.

The script can do the following:

- Rename the font
- Modify hints from font files
- Enable 'legacy', or 'old style' kerning
- Remove PANOSE information
- Add weight to font files

## GUI

Included is a simple GUI wrapper to the script that allows you to choose font files, set options, and generates new
font files.

It is built using PyQt5 or wxPython 3.0.3.

To run the GUI's run either 'ReadifyFont-Qt.py' or 'ReadifyFont-Wx.py'

## CLI

Assuming FontForge is in your system PATH, the script can be invoked like so:

`fontforge -script ReadifyFontCLI.py [OPTIONS] FONT_NAME`

For help, invoke

`fontforge -script ReadifyFontCLI.py -h`

## REQUIREMENTS

A modern version of FontForge. Versions from August 2015 and later have been tested. Note that many linux
distributions (I'm looking at you Ubuntu...) ship an ancient version of FontForge in their repositories.

For the Qt GUI, PyQt5 is required.
