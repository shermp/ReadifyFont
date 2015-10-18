# This script should be called using '$ fontforge -script ReadifyFontCLI.py [OPTIONS] FONTNAME'
#
# Readify Font by Sherman Perry
#
# It has plenty of rough edges...

import os
import sys
import argparse
import fontforge

FNT_REGULAR = 'Regular'
FNT_ITALIC = 'Italic'
FNT_BOLD = 'Bold'
FNT_BOLD_ITALIC = 'BoldItalic'

def changeWeight(glyph, emboldenAmount, modifyBearings):
    origWidth = glyph.width
    glyph.changeWeight(emboldenAmount)
    
    '''
    Change the bearings so that the effective font weight is approximately equal before and after the
    change weight operation.
    
    There has been stability issues observed with the following code (Windows 10 x64). 
    Seems to have happened more with longer output file paths
    Checking if bearingChange>0 seems to have helped. I have not determined the root cause of this, 
    as the python interpreter crashes without providing a traceback
    This stability issue may be Windows related. Or (more likely) I've made a big mistake somewhere...
    '''
    if modifyBearings:
        newWidth = glyph.width
        widthChange = newWidth - origWidth
        bearingChange = widthChange/2
        
        # Try and make this more stable
        if bearingChange > 0:
            glyph.left_side_bearing -= bearingChange
            glyph.right_side_bearing -= bearingChange

def modLayer(glyph):
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
    if stripHints and legacyKern:
        flags = ('opentype', 'old-kern', 'round', 'no-hints')
    elif stripHints and not legacyKern:
        flags = ('opentype', 'round', 'no-hints')
    elif legacyKern and not stripHints:
        flags = ('opentype', 'old-kern', 'round')
    else:
        flags = ('opentype', 'round')
    return flags

    

def setNames(font, family, subfamily):
    # PostScript font names
    fontName = family.replace(' ', '')+'-'+subfamily
    fullName = family + ' ' + subfamily
    # Set PS names
    font.fontname = fontName
    font.familyname = family
    font.fullname = fullName
    # Set SFNT names
    font.appendSFNTName('English (US)', 'Family', unicode(family, 'utf-8'))
    if subfamily == FNT_BOLD_ITALIC:
        font.appendSFNTName('English (US)', 'SubFamily', unicode('Bold Italic', 'utf-8'))
    else:
        font.appendSFNTName('English (US)', 'SubFamily', unicode(subfamily, 'utf-8'))
        font.appendSFNTName('English (US)', 'Fullname', unicode(fullName, 'utf-8'))

parser = argparse.ArgumentParser()
parser.add_argument('fontname', help='Specify new font name')
parser.add_argument('-r', '--regular', help='Regular font file')
parser.add_argument('-i', '--italic' , help='Italic font file')
parser.add_argument('-b', '--bold' , help='bold font file')
parser.add_argument('-B', '--bolditalic' , help='Bold Italic font file')
parser.add_argument('-s', '--striphint' , help='Strip hints from font', action="store_true")
parser.add_argument('-k', '--legacykern' , help='Include legacy kerning table', action="store_true")
parser.add_argument('-d', '--outputdirectory' , help='Output directory if set. Default is "./readified/"')
parser.add_argument('-w', '--addweight' , help='Add weight to font. Values around 8-15 seems suitable. 50 is bold', type=int)
parser.add_argument('-p', '--panosestrip' , help='Strip PANOSE data from font', action="store_true")
parser.add_argument('-m', '--modifybearings' , help='Modify bearings when adding weight. This has no affect when not adding weight. \
                    Only use it for subtle weight changes', action="store_true")
parser.add_argument('-n', '--namehack' , help='If the fonts generated have internal names different to what you specified, \
                    try this option to enable an ugly workaround. It basically generates the font twice.', action="store_true")
args = parser.parse_args()

if not any((args.regular, args.italic, args.bold, args.bolditalic)):
    raw_input('At least one font must be specified. Press ENTER to exit...')
    sys.exit()

fontDic = {FNT_REGULAR : args.regular, FNT_ITALIC : args.italic, FNT_BOLD : args.bold, FNT_BOLD_ITALIC : args.bolditalic}

userSuppliedPath = args.outputdirectory

if userSuppliedPath:
    outDir = userSuppliedPath.strip() + '/'
else:
    outDir = './readified/'

outDir = os.path.normpath(outDir)
print(outDir)
try: 
    os.makedirs(outDir)
except OSError:
    if not os.path.isdir(outDir):
        raise

newFamilyName = args.fontname.strip()
stripHints = args.striphint
legacyKern = args.legacykern
addWeight = args.addweight


for style, fontFile in fontDic.iteritems():
    # Check if a font has been added before proceeding
    if fontFile:
        # Open font file and immediately save as a fontforge file
        f = fontforge.open(fontFile.strip())
        newFontFile = os.path.normpath(outDir+'/'+newFamilyName+'-'+style+'.sfd')
        newFontTTF = os.path.normpath(outDir+'/'+newFamilyName+'-'+style+'.ttf')
        
        f.save(newFontFile)
        f.close()
        
        # Open new fontforge file
        f = fontforge.open(newFontFile)
        
        # Set the font names in the SFNT names table
        setNames(f, newFamilyName, style)
        
        # Replace PANOSE Data with 'Any', or 0
        if args.panosestrip:
            f.os2_panose = (0,0,0,0,0,0,0,0,0,0)
                
        # Iterate over all glyphs in font, and darken regular and italic fonts only
        allGlyphs=f.glyphs()
        for glyph in allGlyphs:
            if style in (FNT_REGULAR, FNT_ITALIC) and addWeight:
                changeWeight(glyph, addWeight, args.modifybearings)
            # Make some modifications to better suit truetype outlines
            modLayer(glyph)
        
        # If I've understood things correctly, this should be the same as setting the curves in the
        # font information screen of the GUI
        for l in range(0, f.layer_cnt):
            if not f.layers[l].is_quadratic:
                f.layers[l].is_quadratic = True
                print('The curves in the '+f.layers[l].name+' layer were converted to be quadratic')
        
        
        print('\nSaving '+newFontTTF+'. . .\n')

        flagsTTF = generateFlags(stripHints, legacyKern)
        f.generate(newFontTTF, flags=flagsTTF)
        
        f.save(newFontFile)
        f.close()
        ''' 
        This is an ugly workaround to the font renaming issue some fonts seem to have
        One day, I hope to find a proper fix, or a more elegent workaround
        '''
        if args.namehack:
            f = fontforge.open(newFontTTF)
            setNames(f, newFamilyName, style)
            f.generate(newFontTTF, flags=flagsTTF)
            f.close()

