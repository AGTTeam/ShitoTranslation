import codecs
from hacktools import common

# The value in pixels that we can fit before wordwrapping
wordwrap = 206
# Speaker codes
speakercodes = {
    0x00: 'Shigeru',
    0x02: 'Asuka',
    0x04: 'Fuyutsuki',
    0x06: 'Gendo',
    0x08: 'Makoto',
    0x0a: 'Hikari',
    0x0c: 'Kaji',
    0x0e: 'Kensuke',
    0x10: 'Maya',
    0x12: 'Misato',
    0x14: 'PenPen',
    0x16: 'Rei',
    0x18: 'Ritsuko',
    0x1a: 'Shinji',
    0x1c: 'Teacher',
    0x1e: 'Toji',
}
# Ranges of strings in other bank files
fileranges = {
    "bank_14.bin": [
        (0x8536, 0x86a6),
        (0x94a2, 0x9990),
        (0xdd74, 0xdd9a),
        (0xddd8, 0xddf2),
        (0xdece, 0xdef2),
        (0xdf30, 0xdf44),
        (0xdfc0, 0xdfd6),
        (0xe020, 0xe034),
    ],
    "bank_1d.bin": [
        (0xce70, 0xdad0),
    ]
}


def convertChar(b1, b2, table):
    char = ""
    if b1 < 0x10:
        char += "0"
    char += format(b1, "x")
    if b2 < 0x10:
        char += "0"
    char += format(b2, "x")
    if char in table:
        charenc = table[char][0]
        if charenc == "":
            return "UNK(" + char + ")", False
        elif charenc == "!":
            return "", False
        else:
            return charenc, False
    return "<" + char + ">", True


def checkStringStart(f, table):
    b2check = f.readByte()
    b1check = f.readByte()
    b2check2 = f.readByte()
    b1check2 = f.readByte()
    f.seek(-4, 1)
    charcheck, charunk = convertChar(b1check, b2check, table)
    if charunk and charcheck in allcodes:
        charunk = False
    charcheck2, charunk2 = convertChar(b1check2, b2check2, table)
    if charunk2 and (charcheck2 in allcodes or charcheck == "<ff06>"):
        charunk2 = False
    if charcheck != "" and charcheck2 != "" and charcheck != "_" and charcheck2 != "_" and not charunk and not charunk2:
        return True
    return False


def readString(f, table, binline=False):
    readingstr = ""
    while True:
        b2 = f.readByte()
        b1 = f.readByte()
        char, _ = convertChar(b1, b2, table)
        if char == "<ffff>":
            break
        elif char == "<ff06>":
            readingstr += "<ch:" + str(f.readUShort()) + ">"
        elif char == "<ff08>":
            readingstr += "<sp:" + str(f.readUShort()) + ">"
        elif char == "<ff0a>":
            readingstr += "<wt:" + str(f.readUShort()) + ">"
        elif char == "<ff0e>":
            readingstr += "<name>"
        elif char == "<ff10>":
            readingstr += "<item>"
        else:
            readingstr += char
    return readingstr


codes = {"<ch:": 0xff06, "<sp:": 0xff08, "<wt:": 0xff0a}
singlecodes = {"name": 0xff0e, "item": 0xff10}
allcodes = ["<ff06>", "<ff08>", "<ff0a>", "<ff0e>", "<ff10>"]


def writeString(f, s, table, bigrams, maxlen=0):
    s = s.replace("～", "〜")
    x = i = 0
    while x < len(s):
        c = s[x]
        if c == "<" and x < len(s) - 4 and s[x:x+4] in codes:
            number = int(s[x+4:].split(">", 1)[0])
            f.writeUShort(codes[s[x:x+4]])
            f.writeUShort(number)
            x += 4 + len(str(number))
            i += 4
        elif c == "<":
            code = s[x+1:].split(">", 1)[0]
            if code in singlecodes:
                f.writeUShort(singlecodes[code])
            else:
                f.writeUShort(int(code, 16))
            x += 1 + len(code)
            i += 2
        elif c == "U" and x < len(s) - 4 and s[x:x+4] == "UNK(":
            code = s[x+6] + s[x+7]
            f.writeByte(int(code, 16))
            code = s[x+4] + s[x+5]
            f.writeByte(int(code, 16))
            x += 8
            i += 2
        elif c == ">" and s[x+1] == ">":
            f.writeUShort(0xff00)
            f.writeUShort(0xff04)
            x += 1
            i += 4
            if len(s) == x + 1:
                # Pad with line breaks
                while i < maxlen:
                    i += 2
                    f.writeUShort(0xff04)
        elif c == "|":
            i += 2
            f.writeUShort(0xff02)
        elif ord(c) < 256:
            if x + 1 == len(s) or ord(s[x+1]) >= 256 or s[x+1] == ">" or s[x+1] == "<" or s[x+1] == "|":
                bigram = c + " "
            else:
                bigram = c + s[x+1]
                x += 1
            if bigram not in bigrams:
                common.logError("Bigram not found:", bigram, "in string", s)
                bigram = "  "
            i += 2
            f.writeUShort(int(bigrams[bigram][0], 16))
        else:
            if c in table:
                f.writeUShort(int(table[c], 16))
            else:
                f.writeUShort(0)
            i += 2
        x += 1
        if maxlen > 0 and i > maxlen:
            common.logError("Line too long", str(i) + "/" + str(maxlen), s)
            i = -1
            break
    return i


def detectTextCode(s, i=0):
    if s[i] == "<":
        return len(s[i:].split(">", 1)[0]) + 1
    elif s[i] == "U" and i < len(s) - 4 and s[i:i+4] == "UNK(":
        return len(s[i:].split(")", 1)[0]) + 1
    elif s[i] == "C" and i < len(s) - 4 and s[i:i+4] == "CUS(":
        return len(s[i:].split(")", 1)[0]) + 1
    return 0


def readFontGlyphs(file):
    glyphs = {}
    with codecs.open(file, "r", "utf-8") as f:
        fontconfig = common.getSection(f, "")
        for c in fontconfig:
            charlen = int(fontconfig[c][0])
            glyphs[c] = common.FontGlyph(0, charlen, charlen + 1)
    return glyphs
