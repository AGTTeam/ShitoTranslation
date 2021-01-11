import codecs
import game
from hacktools import common


def run(data, allfile=False):
    infolder = data + "extract/"
    outfile = data + "bin_output.txt"
    with codecs.open(data + "table_input.txt", "r", "utf-8") as tablef:
        table = common.getSection(tablef, "")
    if allfile:
        game.fileranges = {"bank_1d.bin": [(0x0, 0xfff0)]}

    with codecs.open(outfile, "w", "utf-8") as out:
        common.logMessage("Extracting bin to", outfile, "...")
        for file in common.showProgress(game.fileranges):
            out.write("!FILE:" + file + "\n")
            with common.Stream(infolder + file, "rb") as f:
                for range in game.fileranges[file]:
                    f.seek(range[0])
                    while f.tell() < range[1]:
                        if (len(range) >= 3):
                            f.seek(range[2], 1)
                        pos = f.tell()
                        binstr = game.readString(f, table, True)
                        if allfile and len(binstr) > 50:
                            f.seek(pos + 2)
                            continue
                        if binstr.startswith("|"):
                            f.seek(pos + 2)
                            continue
                        if binstr != "":
                            common.logDebug("Found string at", common.toHex(pos), binstr)
                            out.write(binstr + "=\n")
        common.logMessage("Done!")
