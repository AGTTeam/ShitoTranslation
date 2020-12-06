import codecs
from hacktools import common, ws


def run(data):
    infolder = data + "extract/"
    outfolder = data + "out_IMG/"

    common.logMessage("Extracting images to", outfolder, "...")
    common.makeFolder(outfolder)

    files = common.getFiles(infolder)

    extracted = 0
    with codecs.open(data + "images.txt", "r", "utf-8") as imagef:
        for file in files:
            section = common.getSection(imagef, file)
            with common.Stream(infolder + file, "rb") as f:
                for imgname in section.keys():
                    imgdata = section[imgname][0].split(",")
                    mapstart = int(imgdata[1], 16)
                    imgnum = int(imgdata[2]) if len(imgdata) >= 3 else 1
                    extracted += imgnum
                    if "-" in imgdata[0]:
                        tilestart = int(imgdata[0].split("-")[0], 16)
                        tileend = int(imgdata[0].split("-")[1], 16)
                        for i in common.showProgress(range(tilestart, tileend + 1, 2)):
                            ws.extractMappedImage(f, outfolder + imgname + "_" + hex(i) + ".png", i, mapstart, imgnum)
                    else:
                        tilestart = int(imgdata[0], 16)
                        ws.extractMappedImage(f, outfolder + imgname + ".png", tilestart, mapstart, imgnum)
    common.logMessage("Done! Extracted", extracted, "files")
