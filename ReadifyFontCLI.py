# -*- coding: utf-8 -*-

# This script should be called using "$ fontforge -script ReadifyFontCLI.py [OPTIONS] FONTNAME"
#
# Readify Font by Sherman Perry
#
# It has plenty of rough edges...

from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from helper import *
import fontforge
from fontTools.ttLib import TTFont

if sys.version_info.major == 2:
    PYTHON_TWO = True
else:
    PYTHON_TWO = False
FNT_REGULAR = "Regular"
FNT_ITALIC = "Italic"
FNT_BOLD = "Bold"
FNT_BOLD_ITALIC = "BoldItalic"
OPT_CHANGE_HINT = ("keep", "auto", "remove")

def pyString(uStr):
    if PYTHON_TWO:
        return str(uStr)
    else:
        return uStr

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

def setNames(font, family, subFamily):
    """
    Set font names, both PostScript and TrueType (SFNT names table)
    :param font:
    :param family:
    :param subfam:
    :return:
    """
    # PostScript font names
    fontName = family.replace(" ", "")+"-" + subFamily
    fullName = family + " " + subFamily
    # Set PS names
    font.fontname = fontName
    font.familyname = family
    font.fullname = fullName
    if subFamily == FNT_BOLD_ITALIC:
        subFam = "Bold Italic"
    else:
        subFam = subFamily
    # Set SFNT names
    font.appendSFNTName(tEnc("English (US)"), tEnc("Family"), family)
    font.appendSFNTName(tEnc("English (US)"), tEnc("Preferred Family"), family)
    font.appendSFNTName(tEnc("English (US)"), tEnc("SubFamily"), subFam)
    font.appendSFNTName(tEnc("English (US)"), tEnc("Preferred Styles"), subFam)
    font.appendSFNTName(tEnc("English (US)"), tEnc("Fullname"), fullName)

def getCodePointList(prevText):
    charList = list(set(prevText))
    ordList = []
    for c in charList:
        ordList.append(ord(c))
    return ordList

def modFont(f, newFontFile, newFontTTF, style, newFamilyName, changeHints, legacyKern, addWeight, stripPanose, panoseFix, modBearings, nameHack):
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

    try:
        os.remove(newFontFile)
    except:
        print('There was an error removing the file!')
    """
    This is an ugly workaround to the font renaming issue some fonts seem to have
    One day, I hope to find a proper fix, or a more elegent workaround
    """
    if nameHack:
        f = fontforge.open(newFontTTF)
        setNames(f, newFamilyName, style)
        f.generate(newFontTTF, flags=flagsTTF)
        f.close()

def ConvertSmallcaps(f):
    scGlyphs = []

    for g in f.glyphs():
        scG = False
        gName = g.glyphname
        for st in g.getPosSub("*"):
            if 'smcp' in st[0]:
                scG = True
                scGlyphs.append((gName, st[2]))
                f.selection.select(pyString(st[2]))
                f.copy()
                f.selection.select(pyString(gName))
                f.paste()

                for sc_st in f[st[2].getPosSub("*")]:
                    if 'kern' in sc_st[0]:
                        pass

    return scGlyphs

def removeGlyphs(f, scGlyphs):
    for gN, scN in scGlyphs:
        if scN:
            try:
                f.removeGlyph(-1, scN)
            except ValueError as e:
                pass

def setOS2(newFontTTF, style):
    os2FsSelValues = {FNT_REGULAR : 0x0040, # bit 6 set
                      FNT_ITALIC : 0x0001, # bit 0 set
                      FNT_BOLD : 0x0020, # bit 5 set
                      FNT_BOLD_ITALIC : 0x0021} # bits 0 & 5 set

    os2usWeightClassVals = {FNT_REGULAR : 400,
                      FNT_ITALIC : 400,
                      FNT_BOLD : 700,
                      FNT_BOLD_ITALIC : 700}

    macStyleValues = {FNT_REGULAR : 0x0000, # all bits cleared
                      FNT_ITALIC : 0x0002, # bit 1 set
                      FNT_BOLD : 0x0001, # bit 0 set
                      FNT_BOLD_ITALIC : 0x0003} # bits 0 & 1 set
    tt = TTFont(newFontTTF)
    tt['OS/2'].fsSelection = os2FsSelValues[style]
    tt['OS/2'].usWeightClass = os2usWeightClassVals[style]
    tt['head'].macStyle = macStyleValues[style]
    tt.save(newFontTTF)

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
    parser.add_argument("-P", "--panosefix", help="Attempt to fix PANOSE data for the font", action="store_true")
    parser.add_argument("-m", "--modifybearings" , help="Modify bearings when adding weight. This has no affect when not adding weight. \
                        Only use it for subtle weight changes", action="store_true")
    parser.add_argument("-n", "--namehack" , help="If the fonts generated have internal names different to what you specified, \
                        try this option to enable an ugly workaround. It basically generates the font twice.", action="store_true")
    parser.add_argument("-s", "--smallextract", help="If the font contains small-caps, extract them to a separate smallcaps font file",
                        action="store_true")
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
    smallcapsExtract = args.smallextract
    nameHack = args.namehack

    for style, fontFile in iterDic(fontDic, PYTHON_TWO):
        # Check if a font has been added before proceeding
        if fontFile:
            f = fontforge.open(fontFile.strip())
            newFontFile = os.path.normpath(outDir + "/" + newFamilyName + "-" + style + ".sfd")
            newFontTTF = os.path.normpath(outDir + "/" + newFamilyName + "-" + style + ".ttf")
            f.save(newFontFile)
            f.close()
            f = fontforge.open(newFontFile)
            modFont(f, newFontFile, newFontTTF, style, newFamilyName, changeHints, legacyKern, addWeight, args.panosestrip,
                    args.panosefix, args.modifybearings, nameHack)
            setOS2(newFontTTF, style)

            if smallcapsExtract:
                f = fontforge.open(fontFile.strip())
                scFamilyName = "SC" + newFamilyName
                scFontFile = os.path.normpath(outDir + "/" + scFamilyName + "-" + style + ".sfd")
                scFontTTF = os.path.normpath(outDir + "/" + scFamilyName + "-" + style + ".ttf")
                f.save(scFontFile)
                f.close()
                f = fontforge.open(scFontFile)
                scGlyphs = ConvertSmallcaps(f)
                removeGlyphs(f, scGlyphs)
                tabLiga = "'liga' Standard Ligatures in Latin lookup 6"
                tabSC = "'smcp' Lowercase to Small Capitals in Latin lookup 5"
                f.removeLookup(tabLiga)
                f.removeLookup(tabSC)
                modFont(f, scFontFile, scFontTTF, style, newFamilyName, changeHints, legacyKern, addWeight,
                        args.panosestrip, args.panosefix,
                        args.modifybearings, nameHack)

if __name__ == "__main__":
    main()
