import codecs
import game
from hacktools import common, nasm


def run(data, allfile=False):
    infolder = data + "extract/"
    outfolder = data + "repack/"
    infile = data + "bin_input.txt"
    infilename = data + "name_input.txt"
    chartot = transtot = 0
    table, invtable, ccodes, glyphs = game.getFontData(data)

    with codecs.open(infile, "r", "utf-8") as bin:
        common.logMessage("Repacking bin from", infile, "...")
        for file in common.showProgress(game.fileranges):
            section = common.getSection(bin, file)
            if len(section) == 0:
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            # Repack the file
            common.logMessage("Processing", file, "...")
            common.copyFile(infolder + file, outfolder + file)
            with common.Stream(outfolder + file, "rb+") as f:
                if file != "bank_1d.bin":
                    for binrange in game.fileranges[file]:
                        f.seek(binrange[0])
                        while f.tell() < binrange[1]:
                            if (len(binrange) >= 3):
                                f.seek(binrange[2], 1)
                            strpos = f.tell()
                            readstr = game.readString(f, table, True)
                            if allfile and len(readstr) > 50:
                                f.seek(strpos + 2)
                                continue
                            if readstr.startswith("|"):
                                f.seek(strpos + 2)
                                continue
                            if readstr != "":
                                newstr = ""
                                if readstr in section:
                                    newstr = section[readstr].pop(0)
                                    if len(section[readstr]) == 0:
                                        del section[readstr]
                                strend = f.tell()
                                if newstr != "":
                                    common.logDebug("Repacking", newstr, "at", common.toHex(strpos))
                                    f.seek(strpos)
                                    game.writeString(f, newstr, invtable, ccodes, strend - strpos - 2, True)
                                    while f.tell() < strend:
                                        f.writeByte(int(ccodes[" "][0], 16))
                                    f.seek(strend - 2)
                                    f.writeUShort(0xffff)
                else:
                    # String pointers are stored starting at 0xcd00
                    f.seek(0xcd00)
                    ptrs = []
                    for i in range(23):
                        ptrs.append(f.readUShort())
                        f.seek(14, 1)
                    strings = []
                    for ptr in ptrs:
                        f.seek(ptr)
                        strings.append(game.readString(f, table, True))
                    newptrs = []
                    f.seek(0xce70)
                    for i in range(len(strings)):
                        if strings[i] in section:
                            newstr = section[strings[i]].pop(0)
                        else:
                            newstr = strings[i]
                        newstr = common.wordwrap(newstr, glyphs, game.wordwrap_angel, game.detectTextCode)
                        common.logDebug("Repacking", newstr, "at", common.toHex(f.tell()))
                        newstr = newstr.split("|")
                        if len(newstr) > 8:
                            common.logError("Line too long", str(len(newstr)) + "/8", newstr[0])
                            newstr = newstr[:8]
                        while len(newstr) < 8:
                            newstr.append("")
                        for binstr in newstr:
                            if not binstr.startswith("▼"):
                                binstr = " " + binstr
                            newptrs.append(f.tell())
                            game.writeString(f, binstr, invtable, ccodes, -1, True)
                            f.writeUShort(0xffff)
                    f.seek(0xcd00)
                    for newptr in newptrs:
                        f.writeUShort(newptr)
    # Set the name input selection glyphs in bank 14
    newglyphs = {}
    with codecs.open(infilename, "r", "utf-8") as name:
        nameglyphs = name.read().replace("\r", "").replace("\n", "").replace("#", "")
    with common.Stream(outfolder + "bank_14.bin", "rb+") as f:
        # Write the new name input values
        f.seek(0xc250)
        for nameglyph in nameglyphs:
            if nameglyph in invtable and invtable[nameglyph][:2] != 'ff':
                f.writeUShort(int(invtable[nameglyph], 16))
            else:
                glyphcode = int(ccodes[nameglyph][0], 16) - 0x20
                glyphcode <<= 6
                glyphcode += 0xa300
                newglyphs[nameglyph] = glyphcode
                f.writeUShort(glyphcode)
        # Write "Adam", but using the long glyphs
        f.seek(0x296c + 3)
        f.writeUShort(int(invtable["Ａ"], 16))
        f.seek(3, 1)
        f.writeUShort(newglyphs["d"])
        f.seek(3, 1)
        f.writeUShort(newglyphs["a"])
        f.seek(3, 1)
        f.writeUShort(newglyphs["m"])
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))

    nasm.run(common.bundledFile("bin_patch.asm"))
