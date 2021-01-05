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
            while f.tell() < 0xf9e2:
                b2 = f.readByte()
                b1 = f.readByte()
                utfc, _ = game.convertChar(b1, b2, table)
                if utfc == "<ffff>":
                    out.write("\n")
                else:
                    out.write(utfc)
        common.logMessage("Done!")
