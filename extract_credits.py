import codecs
import game
from hacktools import common


def run(data):
    infolder = data + "extract/"
    outfile = data + "credits_output.txt"
    with codecs.open(data + "table_input.txt", "r", "utf-8") as tablef:
        table = common.getSection(tablef, "")

    with codecs.open(outfile, "w", "utf-8") as out:
        common.logMessage("Extracting credits to", outfile, "...")
        with common.Stream(infolder + "bank_09.bin", "rb") as f:
            f.seek(0xf120)
            readingstr = False
            while f.tell() < 0xf9e2:
                if readingstr:
                    b2 = f.readByte()
                    b1 = f.readByte()
                    if b2 == 0xff and b1 == 0xff:
                        out.write("\n<ffff>")
                        readingstr = False
                    else:
                        out.write(game.convertChar(b1, b2, table))
                else:
                    check = game.checkStringStart(f, table)
                    if check:
                        readingstr = True
                        out.write("\n")
                    else:
                        b2 = f.readByte()
                        b1 = f.readByte()
                        out.write(game.convertChar(b1, b2, table))
        common.logMessage("Done!")
