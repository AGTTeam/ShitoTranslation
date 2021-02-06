import codecs
from PIL import Image
from hacktools import common, ws
import game


def run(data):
    fontfile = data + "font.png"
    fontconfigfile = data + "fontconfig.txt"
    infont = data + "font_output.png"
    outfont = data + "font_input.png"
    outtable = data + "table.txt"
    bankfile = data + "repack/bank_10.bin"

    common.logMessage("Repacking font ...")
    # List of characters and positions in the font.png file
    chars = {}
    positions = {}
    bigrams = []
    with codecs.open(fontconfigfile, "r", "utf-8") as f:
        fontconfig = common.getSection(f, "")
        x = 0
        for c in fontconfig:
            if fontconfig[c][0] == "":
                bigrams.append(c)
                chars[c] = chars[c[0]] + 1 + chars[c[1]]
                continue
            chars[c] = int(fontconfig[c][0])
            positions[c] = x
            if chars[c] > 7:
                x += 15
            else:
                x += 7
    glyphs = game.readFontGlyphs(fontconfigfile)
    skipcodes = [0x0, 0x40, 0x80, 0xc0]

    # Open the images
    img = Image.open(infont).convert("RGB")
    pixels = img.load()
    font = Image.open(fontfile).convert("RGB")
    fontpixels = font.load()

    # Generate the image and table
    fontx = 0
    fonty = 0xa3 * 16 + 1
    fontwidths = []
    x = 0x20
    tablestr = ""
    for item in glyphs:
        while x in skipcodes:
            fontx += 16
            if fontx == 16 * 4:
                fontx = 0
                fonty += 16
            x += 1
            fontwidths.append(0)
        if item in bigrams:
            for i2 in range(7):
                for j2 in range(15):
                    pixels[fontx + i2, fonty + j2] = fontpixels[positions[item[0]] + i2, j2]
            for i2 in range(7):
                for j2 in range(15):
                    pixels[fontx + chars[item[0]] + 1 + i2, fonty + j2] = fontpixels[positions[item[1]] + i2, j2]
        else:
            for i2 in range(15 if chars[item] > 7 else 7):
                for j2 in range(15):
                    pixels[fontx + i2, fonty + j2] = fontpixels[positions[item] + i2, j2]
        if chars[item] < 15:
            for i2 in range(15 - chars[item]):
                for j2 in range(15):
                    pixels[fontx + chars[item] + i2, fonty + j2] = fontpixels[positions[" "], j2]
        fontwidths.append(chars[item] + 1)
        fontx += 16
        if fontx == 16 * 4:
            fontx = 0
            fonty += 16
        tablestr += (item + "=" + common.toHex(x) + "\n")
        x += 1
        if fonty >= img.height:
            break
    with codecs.open(outtable, "w", "utf-8") as f:
        f.write(tablestr)
    # Replace the original ASCII character as well
    fontx = 0
    fonty = 1
    asciiglyphs = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    asciiwidths = []
    for asciiglyph in asciiglyphs:
        for i2 in range(7):
            for j2 in range(15):
                pixels[fontx + i2, fonty + j2] = fontpixels[positions[asciiglyph] + i2, j2]
        for i2 in range(15 - chars[asciiglyph]):
            for j2 in range(15):
                pixels[fontx + chars[asciiglyph] + i2, fonty + j2] = fontpixels[positions[" "], j2]
        asciiwidths.append(chars[asciiglyph] + 1)
        fontx += 16
        if fontx == 16 * 4:
            fontx = 0
            fonty += 16
    img.save(outfont, "PNG")

    # Put the font back in the bank and set the font widths
    with common.Stream(bankfile, "rb+") as f:
        ws.repackTiledImage(f, outfont, 16 * 4, 16 * 244)
        f.seek(0)
        for i in range(len(asciiwidths)):
            f.writeByte(asciiwidths[i])
            f.seek(63, 1)
        f.seek((0xa3 * 4) * 64)
        for i in range(len(fontwidths)):
            if 0x20 + i not in skipcodes:
                f.writeByte(fontwidths[i])
            else:
                f.seek(1, 1)
            f.seek(63, 1)

    common.logMessage("Done!")
