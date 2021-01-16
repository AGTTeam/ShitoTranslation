import codecs
import os
import game
from hacktools import common


def shiftPointers(file, ptrs, pointerdiff):
    with common.Stream(file, "rb+") as f:
        for binptr in ptrs:
            f.seek(binptr[0])
            newpointer = common.shiftPointer(binptr[1], pointerdiff["bank_11.bin" if binptr[2] == 0xf1 else "bank_12.bin"])
            f.writeUShort(newpointer)


def run(data):
    infolder = data + "extract/"
    outfolder = data + "repack/"
    files = ["bank_11.bin", "bank_12.bin"]
    binfile = outfolder + "bank_14.bin"
    debugfile = outfolder + "bank_1e.bin"
    infile = data + "script_input.txt"
    chartot = transtot = 0
    table, invtable, ccodes, glyphs = game.getFontData(data)

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    pointers = {}
    pointerdiff = {}
    common.logMessage("Repacking script from", infile, "...")
    with codecs.open(infile, "r", "utf-8") as script:
        for file in common.showProgress(files):
            section = common.getSection(script, file)
            pointers[file] = []
            pointerdiff[file] = {}
            if len(section) == 0:
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            # Repack the file
            common.logMessage("Processing", file, "...")
            size = os.path.getsize(infolder + file)
            with common.Stream(infolder + file, "rb") as fin:
                with common.Stream(outfolder + file, "wb") as f:
                    while fin.tell() < size:
                        opcode = fin.readByte()
                        if opcode == 0x0a:
                            f.writeByte(opcode)
                            strpos2 = f.tell()
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
                                common.logDebug("Writing string at", common.toHex(strpos), common.toHex(strpos2), newstr)
                                game.writeString(f, newstr, invtable, ccodes)
                                f.writeUShort(0xffff)
                                strend2 = f.tell()
                                lendiff = (strend2 - strpos2) - (strend - strpos)
                                if lendiff != 0:
                                    common.logDebug("Adding", lendiff, "at", common.toHex(strpos))
                                    pointerdiff[file][strpos + 1] = lendiff
                            else:
                                fin.seek(strpos)
                                f.write(fin.read(strend - strpos))
                        elif opcode in game.repopcodes:
                            if opcode in game.ptropcodes:
                                pointers[file].append(f.tell())
                            f.writeByte(opcode)
                            replen = 0
                            while True:
                                loopbyte = fin.readByte()
                                f.writeByte(loopbyte)
                                replen += 1
                                if loopbyte == 0xff and (opcode not in game.ptropcodes or replen > 2):
                                    break
                        else:
                            if opcode in game.ptropcodes:
                                pointers[file].append(f.tell())
                            f.writeByte(opcode)
                            f.write(fin.read(game.opcodes[opcode]))
                            if opcode == 0xff:
                                check = fin.readUInt()
                                check2 = fin.readUInt()
                                fin.seek(-8, 1)
                                if check == 0xffffffff and check2 == 0xffffffff:
                                    break
                    # Pad with 0xffff
                    f.writeBytes(0xff, 0xffff - f.tell() + 1)
    common.logMessage("Shifting script pointers ...")
    for file in common.showProgress(files):
        with common.Stream(outfolder + file, "rb+") as f:
            for pointerpos in pointers[file]:
                f.seek(pointerpos)
                opcode = f.readByte()
                for pointeroff in game.ptropcodes[opcode]:
                    pointerfile = file
                    if type(pointeroff) == tuple:
                        f.seek(pointerpos + 1 + pointeroff[1])
                        bankid = f.readUShort()
                        pointerfile = files[0] if bankid == 0x00f1 else files[1]
                        pointeroff = pointeroff[0]
                    f.seek(pointerpos + 1 + pointeroff)
                    pointer = f.readUShort()
                    if pointer != 0xffff:
                        newpointer = common.shiftPointer(pointer, pointerdiff[pointerfile])
                    else:
                        newpointer = pointer
                    f.seek(-2, 1)
                    f.writeUShort(newpointer)
    common.logMessage("Shifting bin pointers ...")
    # Read pointer tables in the bin file
    with common.Stream(binfile.replace("/repack/", "/extract/"), "rb+") as f:
        f.seek(0x23b0)
        while f.tell() < 0x2740:
            pos1 = f.tell()
            ptr1 = f.readUShort()
            bank1 = f.readUShort()
            pos2 = f.tell()
            ptr2 = f.readUShort()
            bank2 = f.readUShort()
            game.binptrs.append((pos1, ptr1, bank1))
            game.binptrs.append((pos2, ptr2, bank2))
            f.seek(8, 1)
        f.seek(0x902e)
        while f.tell() < 0x9106:
            pos = f.tell()
            ptr = f.readUShort()
            game.binptrs.append((pos, ptr, 0xf2))
    game.binptrs.append((0x26b8, 0x3d7b, 0xf2))
    shiftPointers(binfile, game.binptrs, pointerdiff)
    # Shift debug pointers
    debugptrs = []
    with common.Stream(debugfile.replace("/repack/", "/extract/"), "rb+") as f:
        f.seek(0xcd92)
        while f.tell() < 0xd420:
            pos1 = f.tell()
            ptr1 = f.readUShort()
            bank1 = f.readUShort()
            debugptrs.append((pos1, ptr1, bank1))
            f.seek(12, 1)
    shiftPointers(debugfile, debugptrs, pointerdiff)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
