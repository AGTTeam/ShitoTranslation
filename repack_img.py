import codecs
import game
from hacktools import common, ws


def run(data):
    workfolder = data + "work_IMG/"
    infolder = data + "extract/"
    outfolder = data + "repack/"

    common.logMessage("Repacking images from", workfolder, "...")

    files = common.getFiles(infolder)

    repacked = 0
    with codecs.open(common.bundledFile("images.txt"), "r", "utf-8") as imagef:
        for file in files:
            section = common.getSection(imagef, file)
            if len(section) > 0:
                with common.Stream(outfolder + file, "rb+") as f:
                    for imgname in section.keys():
                        imgdata = section[imgname][0].split(",")
                        mapstart = int(imgdata[1], 16)
                        imgnum = int(imgdata[2]) if len(imgdata) >= 3 else 1
                        readpal = len(imgdata) >= 4 and imgdata[3] == "1"
                        writepal = len(imgdata) >= 5 and imgdata[4] == "1"
                        tilestart = int(imgdata[0], 16)
                        ws.repackMappedImage(f, workfolder + imgname + ".png", tilestart, mapstart, imgnum, readpal, writepal)
                        repacked += imgnum
                    if file == "bank_09.bin":
                        map = game.getBerserkMap(workfolder)
                        ws.repackMappedTiles(f, 0xf080, map, ws.bwpalette)
                        repacked += 1
    # Repack ramen stand images
    with common.Stream(outfolder + "bank_03.bin", "rb+") as f:
        map = game.getRamenMap(workfolder)
        ws.repackMappedTiles(f, 0x3748, map, ws.bwpalette)
        map = game.getLanternMap(workfolder)
        ws.repackMappedTiles(f, 0x3748, map, ws.bwpalette)
        repacked += 2
    common.logMessage("Done! Repacked", repacked, "files")
