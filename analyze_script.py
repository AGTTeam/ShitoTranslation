import codecs
import os
import game
from hacktools import common


def writeLine(out, pos, byte, line):
    out.write(common.toHex(pos).zfill(4) + " 0x" + common.toHex(byte) + ": " + line + "\n")


def run(data, processed):
    infolder = data + ("extract/" if not processed else "repack/")
    files = ["bank_11.bin", "bank_12.bin"]
    outfile = data + "analyze_output.txt"
    with codecs.open(data + "table_input.txt", "r", "utf-8") as tablef:
        table = common.getSection(tablef, "")
    invtable = {}
    with codecs.open(data + "table.txt", "r", "utf-8") as tablef:
        convtable = common.getSection(tablef, "")
        for char in convtable:
            invtable[int(convtable[char][0], 16)] = char

    with codecs.open(outfile, "w", "utf-8") as out:
        for file in common.showProgress(files):
            common.logMessage("Processing", file, "...")
            out.write("!FILE:" + file + "\n")
            size = os.path.getsize(infolder + file)
            with common.Stream(infolder + file, "rb") as f:
                while f.tell() < size - 1:
                    pos = f.tell()
                    opcode = f.readByte()
                    if opcode in game.opcodes and game.opcodes[opcode] != -1:
                        addline = ""
                        if opcode in game.ptropcodes:
                            addline = " Pointer: " + repr(game.ptropcodes[opcode])
                        if opcode == 0x0a:
                            if processed:
                                common.logDebug("Failing at", common.toHex(pos))
                                writeLine(out, pos, opcode, game.readString(f, table, processed=invtable))
                            else:
                                writeLine(out, pos, opcode, game.readString(f, table))
                        elif opcode in game.repopcodes:
                            readbytes = ""
                            replen = 0
                            while True:
                                byte = f.readBytes(1)
                                readbytes += byte
                                replen += 1
                                if byte == "FF " and (opcode not in game.ptropcodes or replen > 2):
                                    break
                            writeLine(out, pos, opcode, readbytes + addline)
                        else:
                            writeLine(out, pos, opcode, f.readBytes(game.opcodes[opcode]) + addline)
                            if opcode == 0xff:
                                out.write("\n")
                                check = f.readUInt()
                                check2 = f.readUInt()
                                f.seek(-8, 1)
                                if check == 0xffffffff and check2 == 0xffffffff:
                                    break
                    else:
                        common.logError("Uknown opcode", common.toHex(opcode), "at", common.toHex(pos))
                        writeLine(out, pos, opcode, "Unknown")
            out.write("\n\n")
        common.logMessage("Done! Extracted", len(files), "files")
