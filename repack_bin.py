import codecs
import game
from hacktools import common


def run(data, allfile=False):
    outfolder = data + "repack/"
    infile = data + "bin_input.txt"
    chartot = transtot = 0
    table, invtable, bigrams, glyphs = game.getFontData(data)

    with codecs.open(infile, "r", "utf-8") as bin:
        common.logMessage("Repacking bin from", infile, "...")
        for file in common.showProgress(game.fileranges):
            section = common.getSection(bin, file)
            if len(section) == 0:
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            # Repack the file
            common.logMessage("Processing", file, "...")
            with common.Stream(outfolder + file, "rb+") as f:
                for range in game.fileranges[file]:
                    f.seek(range[0])
                    while f.tell() < range[1]:
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
                                f.seek(strpos)
                                game.writeString(f, newstr, invtable, bigrams, strend - strpos - 2)
                                f.seek(strend)
        common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
