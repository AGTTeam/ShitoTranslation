import codecs
import os
import game
from hacktools import common


def run(data):
    infolder = data + "extract/"
    files = ["bank_11.bin", "bank_12.bin"]
    outfile = data + "script_output.txt"
    with codecs.open(data + "table_input.txt", "r", "utf-8") as tablef:
        table = common.getSection(tablef, "")

    with codecs.open(outfile, "w", "utf-8") as out:
        common.logMessage("Extracting script to", outfile, "...")
        for file in common.showProgress(files):
            common.logMessage("Processing", file, "...")
            out.write("!FILE:" + file + "\n")
            size = os.path.getsize(infolder + file)
            with common.Stream(infolder + file, "rb") as f:
                lastpos = 0
                while f.tell() < size - 1:
                    b1 = f.readByte()
                    if b1 == 0x0a and game.checkStringStart(f, table):
                        strpos = f.tell()
                        f.seek(lastpos)
                        common.logDebug("Skipped from", lastpos, "to", strpos, ":", f.read(strpos - lastpos).hex())
                        readstr = game.readString(f, table)
                        if readstr != "":
                            if readstr[-2:] == ">>":
                                readstr = readstr[:-2]
                            out.write(readstr)
                            out.write("=\n")
                            common.logDebug("Read string:", readstr)
                            lastpos = f.tell()
            out.write("\n\n")
        common.logMessage("Done! Extracted", len(files), "files")
