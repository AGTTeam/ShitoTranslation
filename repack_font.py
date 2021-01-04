import codecs
from PIL import Image
from hacktools import common, ws
import game


def run(data):
    fontfile = data + "font.png"
    fontconfigfile = data + "fontconfig.txt"
    infont = data + "font_output.png"
    outfont = data + "font_input.png"
    intable = data + "table_output.txt"
    outtable = data + "table.txt"
    eventin = data + "script_input.txt"
    bankfile = data + "repack/bank_10.bin"

    common.logMessage("Repacking font ...")

    # List of characters and positions in the font.png file
    chars = {}
    positions = {}
    with codecs.open(fontconfigfile, "r", "utf-8") as f:
        fontconfig = common.getSection(f, "")
        x = 0
        for c in fontconfig:
            chars[c] = int(fontconfig[c][0])
            positions[c] = x
            if chars[c] > 7:
                x += 15
            else:
                x += 7
    glyphs = game.readFontGlyphs(fontconfigfile)

    # Generate the code range
    codes = []
    skipcodes = []
    with codecs.open(intable, "r", "utf-8") as f:
        table = common.getSection(f, "")
        for c in table:
            charcode = int(c, 16)
            if charcode < 0x900:
                continue
            if charcode == 0x3b40 or charcode == 0x3b80 or charcode == 0xf080:
                skipcodes.append(len(codes))
            codes.append(c)

    # Generate a basic bigrams list
    items = ["  "]
    # And a complete one from all the bigrams
    with codecs.open(eventin, "r", "utf-8") as event:
        inputs = common.getSection(event, "")
    for k, input in inputs.items():
        for str in input:
            if str == "":
                continue
            if str.count("|") == 0:
                str = common.wordwrap(str, glyphs, game.wordwrap, game.detectTextCode)
            str = "<000A>".join(str.replace("|", "<000A>").split(">>"))
            i = 0
            while i < len(str):
                if i < len(str) - 1:
                    nextcode = game.detectTextCode(str, i + 1)
                    if nextcode > 0:
                        str = str[:i+1] + " " + str[i+1:]
                char = str[i]
                textcode = game.detectTextCode(str, i)
                if textcode > 0:
                    i += textcode
                else:
                    if i + 1 == len(str):
                        bigram = char + " "
                    else:
                        bigram = char + str[i+1]
                    i += 2
                    if bigram not in items:
                        if bigram[0] not in chars or bigram[1] not in chars:
                            common.logError("Invalid bigram", bigram, "from phrase", str)
                        else:
                            items.append(bigram)

    # Open the images
    img = Image.open(infont).convert("RGB")
    pixels = img.load()
    font = Image.open(fontfile).convert("RGB")
    fontpixels = font.load()

    # Generate the image and table
    fontx = 0
    fonty = 9 * 16 + 1
    fontwidths = []
    x = 0
    tablestr = ""
    for item in items:
        while x in skipcodes:
            fontx += 16
            x += 1
            fontwidths.append(0)
        if item in chars:
            for i2 in range(15):
                for j2 in range(15):
                    pixels[fontx + i2, fonty + j2] = fontpixels[positions[item] + i2, j2]
            fontwidths.append(chars[item] + 1)
        else:
            for i2 in range(7):
                for j2 in range(15):
                    pixels[fontx + i2, fonty + j2] = fontpixels[positions[item[0]] + i2, j2]
            for j2 in range(15):
                pixels[fontx + chars[item[0]], fonty + j2] = fontpixels[positions[" "], j2]
            for i2 in range(7):
                for j2 in range(15):
                    pixels[fontx + i2 + chars[item[0]] + 1, fonty + j2] = fontpixels[positions[item[1]] + i2, j2]
            totlen = (chars[item[0]] + 1 + chars[item[1]])
            if totlen < 15:
                for i2 in range(15 - totlen):
                    for j2 in range(15):
                        pixels[fontx + totlen + i2, fonty + j2] = fontpixels[positions[" "], j2]
            fontwidths.append(chars[item[0]] + chars[item[1]] + 2)
        fontx += 16
        if fontx == 16 * 4:
            fontx = 0
            fonty += 16
        tablestr += (item + "=" + codes[x] + "\n")
        x += 1
        if fonty >= img.height:
            break
    with codecs.open(outtable, "w", "utf-8") as f:
        f.write(tablestr)
    img.save(outfont, "PNG")

    # Put the font back in the bank and set the font widths
    with common.Stream(bankfile, "rb+") as f:
        ws.repackImage(f, outfont, 16 * 4, 16 * 244)
        f.seek(9 * 4 * 64)
        for i in range(len(fontwidths)):
            if i not in skipcodes:
                f.writeByte(fontwidths[i])
            else:
                f.seek(1, 1)
            f.seek(63, 1)

    if x < len(items):
        common.logMessage("Done! Couldn't fit", len(items) - x, "bigrams")
    else:
        common.logMessage("Done! Room for", len(codes) - x, "more bigrams")
