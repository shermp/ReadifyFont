# -*- coding: utf-8 -*-

# This script should be called using "$ fontforge -script ReadifyFontCLI.py [OPTIONS] FONTNAME"
#
# Readify Font by Sherman Perry
#
# It has plenty of rough edges...

from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import argparse
from helper import *
import fontforge

if sys.version_info.major == 2:
    PYTHON_TWO = True
else:
    PYTHON_TWO = False
FNT_REGULAR = "Regular"
FNT_ITALIC = "Italic"
FNT_BOLD = "Bold"
FNT_BOLD_ITALIC = "BoldItalic"
OPT_CHANGE_HINT = ("keep", "auto", "remove")

def tEnc(unicodeString):
    """
    Many FontForge methods will not except unicode... except when they do, and are required.
    Returns an unmodified unicode object if python 3 is the interpreter.
    :param unicodeString:
    :return:
    """
    if PYTHON_TWO:
        return unicodeString.encode(encoding="utf-8")
    else:
        return unicodeString

def changeWeight(glyph, emboldenAmount, modifyBearings):
    """
    Change the weight of the glyph by an amount chosen by the user. Optionally modify the left and right bearings as
    well.
    :param glyph:
    :param emboldenAmount:
    :param modifyBearings:
    :return:
    """
    origWidth = glyph.width
    glyph.changeWeight(emboldenAmount)
    
    """
    Change the bearings so that the effective font weight is approximately equal before and after the
    change weight operation.
    
    There has been stability issues observed with the following code (Windows 10 x64). 
    Seems to have happened more with longer output file paths
    Checking if bearingChange>0 seems to have helped. I have not determined the root cause of this, 
    as the python interpreter crashes without providing a traceback
    This stability issue may be Windows related. Or (more likely) I"ve made a big mistake somewhere...
    """
    if modifyBearings:
        newWidth = glyph.width
        widthChange = newWidth - origWidth
        bearingChange = widthChange/2
        
        # Try and make this more stable
        if bearingChange > 0:
            glyph.left_side_bearing -= bearingChange
            glyph.right_side_bearing -= bearingChange

def modLayer(glyph):
    """
    Close contours/open paths in a glyh if requred, and ensure directions are correct.
    :param glyph:
    :return:
    """
    # Get active layer object
    lay = glyph.layers[glyph.activeLayer]
    
    # get iterator of contours
    contours = lay.__iter__()
    
    # for any open contours, close them
    for c in contours:
        if not c.closed:
            c.closed=True
    
    # Assign the modified layer object back to the glyph
    glyph.layers[glyph.activeLayer] = lay
    glyph.correctDirection()

def generateFlags(stripHints, legacyKern):
    """
    Generate flags for TrueType font generation, based on options chosen by the user.
    :param stripHints:
    :param legacyKern:
    :return:
    """
    if stripHints == "remove" and legacyKern:
        flags = (tEnc("opentype"), tEnc("old-kern"), tEnc("round"), tEnc("no-hints"))
    elif stripHints == "remove" and not legacyKern:
        flags = (tEnc("opentype"), tEnc("round"), tEnc("no-hints"))
    elif legacyKern and stripHints == "keep":
        flags = (tEnc("opentype"), tEnc("old-kern"), tEnc("round"))
    else:
        flags = (tEnc("opentype"), tEnc("round"))
    return flags

    

def setNames(font, family, subfamily):
    """
    Set font names, both PostScript and TrueType (SFNT names table)
    :param font:
    :param family:
    :param subfamily:
    :return:
    """
    # PostScript font names
    fontName = family.replace(" ", "")+"-"+subfamily
    fullName = family + " " + subfamily
    # Set PS names
    font.fontname = fontName
    font.familyname = family
    font.fullname = fullName
    # Set SFNT names
    font.appendSFNTName(tEnc("English (US)"), tEnc("Family"), family)
    if subfamily == FNT_BOLD_ITALIC:
        font.appendSFNTName(tEnc("English (US)"), tEnc("SubFamily"), "Bold Italic")
    else:
        font.appendSFNTName(tEnc("English (US)"), tEnc("SubFamily"), subfamily)
        font.appendSFNTName(tEnc("English (US)"), tEnc("Fullname"), fullName)

def getCodePointList(prevText):
    charList = list(set(prevText))
    ordList = []
    for c in charList:
        ordList.append(ord(c))
    return ordList

def modFont(fontFile, style, outDir, newFamilyName, changeHints, legacyKern, addWeight, stripPanose, modBearings,
            nameHack, preview):
    # Open font file and immediately save as a fontforge file
    f = fontforge.open(fontFile.strip())
    newFontFile = os.path.normpath(outDir+"/"+newFamilyName+"-"+style+".sfd")
    newFontTTF = os.path.normpath(outDir+"/"+newFamilyName+"-"+style+".ttf")
    if preview:
        cpList = getCodePointList(preview)
        if cpList:
            for cp in cpList:
                f.selection.select((tEnc("more"), None), cp)
        else:
             f.selection.select((tEnc("ranges"), None), tEnc("A"),tEnc("z"))
        f.copy()

        n = fontforge.font()
        if cpList:
            for cp in cpList:
                n.selection.select((tEnc("more"), None), cp)
        else:
            n.selection.select((tEnc("ranges"), None), tEnc("A"),tEnc("z"))
        n.paste()

        n.fontname="RF-Prev-"+style
        n.save(newFontFile)
    else:
        f.save(newFontFile)
    f.close()

    # Open new fontforge file
    f = fontforge.open(newFontFile)

    # Set the font names in the SFNT names table
    setNames(f, newFamilyName, style)

    # Replace PANOSE Data with "Any", or 0
    if stripPanose:
        f.os2_panose = (0,0,0,0,0,0,0,0,0,0)

    # Iterate over all glyphs in font, and darken regular and italic fonts only
    allGlyphs=f.glyphs()
    for glyph in allGlyphs:
        if style in (FNT_REGULAR, FNT_ITALIC) and addWeight:
            changeWeight(glyph, addWeight, modBearings)
        # Make some modifications to better suit truetype outlines
        modLayer(glyph)
        # Autohint glyph
        if changeHints == "auto":
            glyph.autoHint()

    # If I've understood things correctly, this should be the same as setting the curves in the
    # font information screen of the GUI
    for l in range(0, f.layer_cnt):
        if not f.layers[l].is_quadratic:
            f.layers[l].is_quadratic = True
            print("The curves in the "+f.layers[l].name+" layer were converted to be quadratic")

    print("\nSaving "+newFontTTF+". . .\n")

    flagsTTF = generateFlags(changeHints, legacyKern)
    f.generate(newFontTTF, flags=flagsTTF)

    f.save(newFontFile)
    f.close()
    """
    This is an ugly workaround to the font renaming issue some fonts seem to have
    One day, I hope to find a proper fix, or a more elegent workaround
    """
    if nameHack:
        f = fontforge.open(newFontTTF)
        setNames(f, newFamilyName, style)
        f.generate(newFontTTF, flags=flagsTTF)
        f.close()

def main():
    """
    The main function of the script that modifies fonts according to user options
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("fontname", help="Specify new font name")
    parser.add_argument("-r", "--regular", help="Regular font file")
    parser.add_argument("-i", "--italic" , help="Italic font file")
    parser.add_argument("-b", "--bold" , help="bold font file")
    parser.add_argument("-B", "--bolditalic" , help="Bold Italic font file")
    parser.add_argument("-c", "--changehint" , help="Choose whether to keep hints, remove hints, or enable autohinting.\n"
                        "allowed arguments are \"keep\", \"remove\", \"auto\". Keep is the default.", type=str)
    parser.add_argument("-k", "--legacykern" , help="Include legacy kerning table", action="store_true")
    parser.add_argument("-d", "--outputdirectory" , help="Output directory if set. Default is \"./readified/\"")
    parser.add_argument("-w", "--addweight" , help="Add weight to font. Values around 8-15 seems suitable. 50 is bold", type=int)
    parser.add_argument("-p", "--panosestrip" , help="Strip PANOSE data from font", action="store_true")
    parser.add_argument("-m", "--modifybearings" , help="Modify bearings when adding weight. This has no affect when not adding weight. \
                        Only use it for subtle weight changes", action="store_true")
    parser.add_argument("-n", "--namehack" , help="If the fonts generated have internal names different to what you specified, \
                        try this option to enable an ugly workaround. It basically generates the font twice.", action="store_true")
    parser.add_argument("-P", "--previewfont", help="If specified, a preview font file will be generated in the "
                                                  "directory "
                                              "set by \"--previewdirectory\".\nAt least one of regular or italic font "
                                              "files should be added. The default preview order is \"regular\", "
                                              "\"italic\"")
    parser.add_argument("-D", "--previewdirectory", help="The directory to store the preview font. If this is omitted, "
                                                   "no preview will be generated.")
#    parser.add_argument("-T", "--previewtext", help="Characters that will be used for font preview")

    args = parser.parse_args()

    if not any((args.regular, args.italic, args.bold, args.bolditalic)):
        input("At least one font must be specified. Press ENTER to exit...")
        sys.exit()

    fontDic = {FNT_REGULAR : args.regular, FNT_ITALIC : args.italic, FNT_BOLD : args.bold, FNT_BOLD_ITALIC : args.bolditalic}

    userSuppliedPath = args.outputdirectory

    if userSuppliedPath:
        outDir = userSuppliedPath.strip() + "/"
    else:
        outDir = "./readified/"

    outDir = os.path.normpath(outDir)
    print(outDir)
    try:
        os.makedirs(outDir)
    except OSError:
        if not os.path.isdir(outDir):
            raise

    newFamilyName = args.fontname.strip()
    changeHints = args.changehint

    if not changeHints:
        changeHints = "keep"
    else:
        changeHints = changeHints.strip()
        changeHints = changeHints.lower()
        if changeHints not in OPT_CHANGE_HINT:
            changeHints = "keep"
            print("You did not specify a correct hint argument. Current hints will be preserved.")

    legacyKern = args.legacykern
    addWeight = args.addweight

    if args.previewfont and args.previewdirectory and (fontDic[FNT_REGULAR] or fontDic[FNT_ITALIC]):
        prevOutDir = args.previewdirectory.strip()
        prevFamilyName = "preview"
        if fontDic[FNT_REGULAR]:
            prevFontFile = fontDic[FNT_REGULAR]
            prevStyle = FNT_REGULAR
            modFont(prevFontFile, prevStyle, prevOutDir, prevFamilyName, changeHints, legacyKern, addWeight,
                    args.panosestrip, args.modifybearings, args.namehack, preview=args.previewfont.strip())
        if fontDic[FNT_ITALIC]:
            prevFontFile = fontDic[FNT_ITALIC]
            prevStyle = FNT_ITALIC
            modFont(prevFontFile, prevStyle, prevOutDir, prevFamilyName, changeHints, legacyKern, addWeight,
                    args.panosestrip, args.modifybearings, args.namehack, preview=args.previewfont.strip())

    else:
        for style, fontFile in iterDic(fontDic, PYTHON_TWO):
            # Check if a font has been added before proceeding
            if fontFile:
                modFont(fontFile, style, outDir, newFamilyName, changeHints, legacyKern, addWeight, args.panosestrip,
                        args.modifybearings, args.namehack, preview=None)

if __name__ == "__main__":
    main()
