import codecs
from hacktools import common

# The value in pixels that we can fit before wordwrapping
wordwrap = 206
wordwrap_angel = 136
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
        (0xb715, 0xb909, 2),
        (0x94a2, 0x9990),
        (0xa380, 0xa388),
        (0xa390, 0xa396),
        (0xa3a0, 0xa3aa),
        (0xa3b0, 0xa3b6),
        (0xa3c0, 0xa3c6),
        (0x5384, 0x5388),
        (0x5394, 0x539d),
        (0x53a4, 0x53ad),
        (0x53b4, 0x53bd),
        (0x53c4, 0x53cd),
        (0x5640, 0x5643),
        (0x5650, 0x5659),
        (0x5660, 0x5669),
        (0x5670, 0x5679),
        (0x5680, 0x5689),
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
# Script opcodes
# The comments are the addresses in the jump table that is used for script opcodes
# A value of -1 means the size is not known
opcodes = {
    0x00: 2,   # 0x7452 ?
    0x02: 2,   # 0x7468 ?
    0x04: 2,   # 0x748f ?
    0x06: 2,   # 0x7496 ?
    0x08: 0,   # 0x749d ?
    0x0a: 0,   # 0x74c9 String, read words until 0xffff
    0x0c: 0,   # 0x74d6 ?
    0x0e: 0,   # 0x74e3 ?
    0x10: 4,   # 0x74ed Portrait
    0x12: 0,   # 0x750a ?
    0x14: 2,   # 0x7513 ?
    0x16: 0,   # 0x7576 ?
    0x18: 2,   # 0x75E6 ?
    0x1a: 0,   # 0x764D Jumps to 0x16
    0x1c: 0,   # 0x7650 ?
    0x1e: 0,   # 0x76BC ?
    0x20: 0,   # 0x7723 ?
    0x22: 5,   # 0x77A2 ?
    0x24: 7,   # 0x77BD Jump?
    0x26: 2,   # 0x77EC ?
    0x28: 4,   # 0x77FF ?
    0x2a: 4,   # 0x7823 ?
    0x2c: 4,   # 0x7847 ?
    0x2e: 4,   # 0x786B ?
    0x30: 3,   # 0x788F ?
    0x32: 4,   # 0x78AC ?
    0x34: 4,   # 0x78C7 ?
    0x36: 4,   # 0x78E2 Jump?
    0x38: 2,   # 0x78FD ?
    0x3a: 8,   # 0x790B ?
    0x3c: 4,   # 0x793F ?
    0x3e: 0,   # 0x7987 ?
    0x40: 6,   # 0x7993 Jump?
    0x42: 0,   # 0x79B9 ?
    0x44: 4,   # 0x79C5 Jump?
    0x46: 0,   # 0x79DF ?
    0x48: 2,   # 0x79FD Jump?
    0x4a: 4,   # 0x7A07 Choice jump?
    0x4c: 4,   # 0x7AF4 2 jumps?
    0x4e: 1,   # 0x7CBA ?
    0x50: 1,   # 0x7CCC ?
    0x52: 0,   # 0x7CE0 ? call 7c2c and read bytes until 0xff
    0x54: 0,   # 0x7CEA ? call 7c41 and read bytes until 0xff
    0x56: 0,   # 0x7CF4 ? +3, call 7c58 and read bytes until 0xff
    0x58: 3,   # 0x7D09 Jump?
    0x5a: 3,   # 0x7D27 Operator jump?
    0x5c: 3,   # 0x7D44 Jump?
    0x5e: 3,   # 0x7D61 Jump?
    0x60: 4,   # 0x7D7D Jump?
    0x62: 1,   # 0x7D9D ?
    0x64: 1,   # 0x7DC9 ?
    0x66: 3,   # 0x7E16 Jump?
    0x68: 3,   # 0x7E37 Jump?
    0x6a: 5,   # 0x7E58 Jump?
    0x6c: 8,   # 0x7E86 Jump?
    0x6e: 3,   # 0x7EBE Jump?
    0x70: 1,   # 0x7EDC ?
    0x72: 2,   # 0x7F01 ?
    0x74: 2,   # 0x7F24 ?
    0x76: 2,   # 0x7F2E ?
    0x78: 2,   # 0x7F3E ?
    0x7a: 0,   # 0x7F4E ? +6, call 7c58 and read bytes until 0xff
    0x7c: 0,   # 0x7FBA ? +3, call 7c2c and read bytes until 0xff
    0x7e: 0,   # 0x7FEE ? +2, call 7c41 and read bytes until 0xff
    0x80: 0,   # 0x8018 ? +2, call 7c41 and read bytes until 0xff
    0x82: 1,   # 0x803D ?
    0x84: 1,   # 0x8052 ?
    0x86: 2,   # 0x8067 ?
    0x88: 2,   # 0x807D ?
    0x8a: 2,   # 0x8093 ?
    0x8c: 2,   # 0x80A9 ?
    0x8e: 0,   # 0x80BF ?
    0x90: 3,   # 0x80DA Jump?
    0x92: 4,   # 0x80F8 Jump?
    0x94: 4,   # 0x8113 Jump?
    0x96: 4,   # 0x812E Jump?
    0x98: 2,   # 0x8149 Jump?
    0x9a: 6,   # 0x8162 ?
    0x9c: 2,   # 0x818D ?
    0x9e: 4,   # 0x81A0 ?
    0xa0: 0,   # 0x81B7 ?
    0xa2: 4,   # 0x81C6 ?
    0xa4: 0,   # 0x81DD ?
    0xa6: 0,   # 0x81EC ?
    0xa8: 5,   # 0x81FB ?
    0xaa: 0,   # 0x8219 ?
    0xac: 0,   # 0x8226 ?
    # The ones below are not actually used in any script
    0xae: 1,   # 0x8233 ?
    0xb0: 1,   # 0x8243 ?
    0xb2: 2,   # 0x8253 ?
    0xb4: 1,   # 0x8261 ?
    0xb6: 2,   # 0x8273 ?
    0xb8: 2,   # 0x8281 ?
    0xff: 1,   # END, 0xffff
}
# Repeat opcodes
repopcodes = [0x52, 0x54, 0x56, 0x7a, 0x7c, 0x7e, 0x80]
# Pointer opcodes with list of pointer offsets after the opcode
ptropcodes = {
    0x24: [5],
    0x36: [2],
    0x40: [(4, 2)],
    0x44: [(0, 2)],
    0x48: [0],
    0x4a: [0],
    0x4c: [0, 2],
    0x56: [0],
    0x58: [0],
    0x5a: [0],
    0x5c: [0],
    0x5e: [0],
    0x60: [0],
    0x66: [0],
    0x68: [0],
    0x6a: [0],
    0x6c: [0],
    0x6e: [0],
    0x7a: [0],
    0x90: [0],
    0x92: [0],
    0x94: [0],
    0x96: [0],
    0x98: [0],
}
# A list of hardcoded script pointers found in the binary file
# Format: (offset, ptr value, bank value)
# Mostly "mov word ptr ds:0x1697, value" opcodes
# and "mov ax, value / mov word ptr ds:0x149f, ax"
binptrs = [
    (0x2da3+1, 0x788f, 0xf2),
    (0x2dc1+1, 0x788f, 0xf2),
    (0x30b7+1, 0x8e2f, 0xf2),
    (0x30c1+1, 0x8f5d, 0xf2),
    (0x441b+1, 0xa8d0, 0xf2),
    (0x445a+1, 0xa99d, 0xf2),
    (0x4499+1, 0xaa60, 0xf2),
    (0x44d2+1, 0xaad7, 0xf2),
    (0x44e4+1, 0xabaa, 0xf2),
    (0x45ac+1, 0x938c, 0xf2),
    (0x4646+1, 0x9031, 0xf2),
    (0x46b1+1, 0x9296, 0xf2),
    (0x46eb+1, 0x92e2, 0xf2),
    (0x4703+1, 0x934b, 0xf2),
    (0x47ae+1, 0xb4ba, 0xf2),
    (0x4860+1, 0x93f8, 0xf2),
    (0x5a73+4, 0xa69f, 0xf2),
    (0x5a99+4, 0xa6f5, 0xf2),
    (0x5abf+4, 0xa88e, 0xf2),
    (0x8d29+1, 0x0f34, 0xf1),
    (0xf029+4, 0x94cd, 0xf2),
    (0xf065+4, 0x94d6, 0xf2),
    (0xf12a+4, 0x970f, 0xf2),
    (0xf1de+4, 0x981a, 0xf2),
    (0xf292+4, 0x99b5, 0xf2),
    (0xf32c+4, 0x9b7a, 0xf2),
    (0xf3fc+4, 0x9dec, 0xf2),
    (0xf41b+4, 0xa069, 0xf2),
    (0xf443+4, 0xa08a, 0xf2),
    (0xf461+4, 0xa0f4, 0xf2),
    (0xf48c+4, 0xa140, 0xf2),
    (0xf4bc+4, 0xa19c, 0xf2),
    (0xf4ec+4, 0xa24e, 0xf2),
    (0xf520+4, 0xa2de, 0xf2),
    (0xf550+4, 0xa3c0, 0xf2),
    (0xf56f+4, 0xa2fc, 0xf2),
    (0xf599+4, 0xa30b, 0xf2),
    (0xf5b5+4, 0xa411, 0xf2),
    (0xf630+4, 0xa46d, 0xf2),
    (0xf673+4, 0xa625, 0xf2),
    (0xf6a2+4, 0xa66e, 0xf2),
    (0xf72e+4, 0xa7fa, 0xf2),
    (0xf746+4, 0xa853, 0xf2),
]


def getFontData(data):
    fontconfig = data + "fontconfig.txt"
    with codecs.open(data + "table_input.txt", "r", "utf-8") as tablef:
        table = common.getSection(tablef, "")
    invtable = {}
    for c in table.keys():
        invtable[table[c][0]] = c
    with codecs.open(data + "table.txt", "r", "utf-8") as tablef:
        ccodes = common.getSection(tablef, "")
    glyphs = readFontGlyphs(fontconfig)
    return table, invtable, ccodes, glyphs


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


def readString(f, table, binline=False, processed=None):
    readingstr = ""
    while True:
        b2 = f.readByte()
        if processed is not None and b2 >= 0x20 and b2 != 0x40 and b2 != 0x80 and b2 < 0xc0 and b2 in processed:
            readingstr += processed[b2]
            continue
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
        elif char == "<ff0c>":
            readingstr += "<unk1>"
        elif char == "<ff0e>":
            readingstr += "<name>"
        elif char == "<ff10>":
            readingstr += "<item>"
        elif char == "<ff12>":
            readingstr += "<angl>"
        elif char == "<ff14>":
            readingstr += "<perc>"
        else:
            readingstr += char
    return readingstr


codes = {"<ch:": 0xff06, "<sp:": 0xff08, "<wt:": 0xff0a}
singlecodes = {"unk1": 0xff0c, "name": 0xff0e, "item": 0xff10, "angl": 0xff12, "perc": 0xff14}
allcodes = ["<ff06>", "<ff08>", "<ff0a>", "<ff0c>", "<ff0e>", "<ff10>", "<ff12>", "<ff14>"]


def writeString(f, s, table, ccodes, maxlen=0, usebigrams=False):
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
        elif c == "|":
            i += 2
            f.writeUShort(0xff02)
        elif c in ccodes or ord(c) < 256:
            i += 1
            if c not in ccodes:
                common.logError("Character not found:", c, "in string", s)
                c = " "
            if x < len(s) - 1 and c + s[x+1] in ccodes:
                f.writeByte(int(ccodes[c + s[x+1]][0], 16))
                x += 1
            else:
                f.writeByte(int(ccodes[c][0], 16))
        else:
            if c in table:
                f.writeUShort(int(table[c], 16))
            else:
                f.writeUShort(0)
            i += 2
        x += 1
        if maxlen > 0 and i > maxlen:
            common.logError("Line too long", str(i) + "/" + str(len(s) - x) + "/" + str(maxlen), s)
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
            charlen = 0 if fontconfig[c][0] == "" else int(fontconfig[c][0])
            glyphs[c] = common.FontGlyph(0, charlen, charlen + 1)
    return glyphs
