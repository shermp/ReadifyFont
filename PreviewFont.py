import os
import wx
import wx.html2
import urlparse, urllib

class PreviewContent():
    previewDir = ""
    previewFontList = []
    origFontDic = None
    previewText = ""

    def __init__(self, previewDir, origFontDic, previewText):
        self.previewDir = previewDir
        self.origFontDic = origFontDic
        self.previewText = previewText
        if self.previewDir:
            for f in os.listdir(self.previewDir):
                if f.endswith(".ttf"):
                    self.previewFontList.append(f)

    def path2url(self, path):
        return urlparse.urljoin('file:', urllib.pathname2url(path))

    def genhtmlcss(self):
        if self.previewFontList:
            fontFaceCSS = ""
            paragraphCSS = ""
            for font in self.previewFontList:
                if "regular" in font.lower():
                    tempFaceCSS = "@font-face {{ font-family: 'preview'; font-weight: normal; font-style: normal; " \
                                   "src: url('{0}'); }}\n"
                    previewFontPath = os.path.normpath(self.previewDir + "/" + font)
                    fontFaceCSS += tempFaceCSS.format(self.path2url(previewFontPath))
                elif "italic" in font.lower():
                    tempFaceCSS = "@font-face {{ font-family: 'preview'; font-weight: normal; font-style: italic; " \
                                   "src: url('{0}'); }}\n"
                    previewFontPath = os.path.normpath(self.previewDir + "/" + font)
                    fontFaceCSS = tempFaceCSS.format(self.path2url(previewFontPath))

            print(fontFaceCSS)
            for style, font in self.origFontDic.iteritems():
                if style.lower() == "regular":
                    tempFaceCSS = "@font-face {{ font-family: 'original'; font-weight: normal; font-style: normal; " \
                                   "src: url('{0}'); }}\n"
                    origFontPath = os.path.normpath(font)
                    fontFaceCSS += tempFaceCSS.format(self.path2url(origFontPath))
                elif style.lower() == "italic":
                    tempFaceCSS = "@font-face {{ font-family: 'original'; font-weight: normal; font-style: italic; " \
                                   "src: url('{0}'); }}\n"
                    origFontPath = os.path.normpath(font)
                    fontFaceCSS += tempFaceCSS.format(self.path2url(origFontPath))

            for font in self.previewFontList:
                if "regular" in font.lower():
                    paragraphCSS += "p.prevReg { font-family: 'preview'; font-size: 20pt; }\n"
                elif "italic" in font.lower():
                    paragraphCSS += "p.prevIta { font-family: 'preview'; font-style: italic; font-size: 20pt; }\n"

            for style, font in self.origFontDic.iteritems():
                if style.lower() == "regular":
                    paragraphCSS += "p.origReg { font-family: 'original'; font-size: 20pt; }\n"
                elif style.lower() == "italic":
                    paragraphCSS += "p.origIta { font-family: 'original'; font-style: italic; font-size: 20pt; }\n"

            html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
            <html>
                <head>
                    <title>Font Preview</title>
                    <style type="text/css">
                        {0}
                    </style>
                </head>
                <body>
                    <table style="width: 100%;">
                        <tr>
                            <td>Original Font</td>
                            <td>Preview Font</td>
                        </tr>
                        <tr>
                            <td>{1}</td>
                            <td>{2}</td>
                        </tr>
                        <tr>
                            <td>{3}</td>
                            <td>{4}</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            css = fontFaceCSS + paragraphCSS
            origRegText = "<p class=\"origReg\">" + self.previewText + "</p>"
            prevRegText = "<p class=\"prevReg\">" + self.previewText + "</p>"
            origItaText = "<p class=\"origIta\">" + self.previewText + "</p>"
            prevItaText = "<p class=\"prevIta\">" + self.previewText + "</p>"
            html = html.format(css, origRegText, prevRegText, origItaText, prevItaText)
            return html
"""
The following code has been adapted from http://stackoverflow.com/a/10866495
"""
class PreviewWindow(wx.Dialog):
    def __init__(self, *args, **kwds):
        wx.Dialog.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.SetSize((700, 400))