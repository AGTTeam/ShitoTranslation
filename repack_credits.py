import codecs
import os
import game
from hacktools import common


def run(data):
    bank = data + "repack/bank_09.bin"
    infile = data + "credits_input.txt"
    table, invtable, bigrams, glyphs = game.getFontData(data)

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.logMessage("Repacking credits from", infile, "...")
    with codecs.open(infile, "r", "utf-8") as credits:
        credstr = credits.read()
    with common.Stream(bank, "rb+") as f:
        f.seek(0xf120)
        game.writeString(f, credstr.replace("\n", "<ffff>"), invtable, bigrams)
        # Pad with ffff
        while f.tell() < 0xffff:
            f.writeUShort(0xffff)
    common.logMessage("Done!")
