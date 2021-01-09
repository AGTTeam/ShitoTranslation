import codecs
import os
import game
from hacktools import common


def run(data):
    infolder = data + "extract/"
    outfolder = data + "repack/"
    files = ["bank_11.bin", "bank_12.bin"]
    infile = data + "script_input.txt"
    chartot = transtot = 0
    table, invtable, ccodes, glyphs = game.getFontData(data)

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.logMessage("Repacking script from", infile, "...")
    with codecs.open(infile, "r", "utf-8") as script:
        for file in common.showProgress(files):
            section = common.getSection(script, file)
            if len(section) == 0:
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            allempty = True
            for check in section:
                for check2 in section[check]:
                    if check2 != "":
                        allempty = False
                        break
            if allempty:
                continue
            # Repack the file
            common.logMessage("Processing", file, "...")
            size = os.path.getsize(infolder + file)
            with common.Stream(infolder + file, "rb") as fin:
                with common.Stream(outfolder + file, "wb") as f:
                    while fin.tell() < size:
                        b1 = fin.readByte()
                        if b1 == 0x0a and game.checkStringStart(fin, table):
                            f.writeByte(b1)
                            strpos = fin.tell()
                            readstr = game.readString(fin, table)
                            newstr = ""
                            if readstr != "":
                                addend = ""
                                if readstr[-2:] == ">>":
                                    addend = ">>"
                                    readstr = readstr[:-2]
                                if readstr in section:
                                    newstr = section[readstr].pop(0)
                                    if len(section[readstr]) == 0:
                                        del section[readstr]
                            strend = fin.tell()
                            if newstr != "":
                                if newstr.count("|") == 0:
                                    newstr = common.wordwrap(newstr, glyphs, game.wordwrap, game.detectTextCode)
                                if newstr == "!":
                                    newstr = ""
                                newstr += addend
                                game.writeString(f, newstr, invtable, ccodes, strend - strpos - 2)
                                f.seek(strend - 2)
                                f.writeUShort(0xffff)
                            else:
                                fin.seek(strpos)
                                f.write(fin.read(strend - strpos))
                        else:
                            f.writeByte(b1)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
