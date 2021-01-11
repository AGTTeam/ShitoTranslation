import codecs
import os
import game
from hacktools import common


def run(data, speaker=True, scene=False, merge=False):
    infolder = data + "extract/"
    files = ["bank_11.bin", "bank_12.bin"]
    outfile = data + "script_output.txt"
    with codecs.open(data + "table_input.txt", "r", "utf-8") as tablef:
        table = common.getSection(tablef, "")
    if merge:
        mergescript = codecs.open(data + "script_input.txt", "r", "utf-8")

    # Get the scenes list from the debug menu
    if scene:
        scenenames = {"bank_11.bin": [], "bank_12.bin": []}
        with common.Stream(infolder + "bank_1e.bin", "rb") as f:
            f.seek(0xcd90)
            while True:
                unk = f.readUShort()
                if unk == 0xffff:
                    break
                scenepos = f.readUShort()
                scenebank = "bank_11.bin" if f.readUShort() == 0x00f1 else "bank_12.bin"
                scenename = f.readNullString()
                scenenames[scenebank].append({'pos': scenepos, 'name': scenename})
                f.seek(1, 1)  # Always 0x90
        for bankname in scenenames:
            scenenames[bankname] = sorted(scenenames[bankname], key=lambda i: i['pos'])

    # Extract the scripts
    with codecs.open(outfile, "w", "utf-8") as out:
        common.logMessage("Extracting script to", outfile, "...")
        for file in common.showProgress(files):
            common.logMessage("Processing", file, "...")
            out.write("!FILE:" + file + "\n")
            size = os.path.getsize(infolder + file)
            lastspeaker = -1
            if scene:
                nextscene = scenenames[file].pop(0)
            if merge:
                mergesection = common.getSection(mergescript, file)
            with common.Stream(infolder + file, "rb") as f:
                while f.tell() < size - 1:
                    opcode = f.readByte()
                    if opcode == 0x0a:
                        strpos = f.tell()
                        # Print the scene name
                        if scene:
                            if (nextscene is not None and strpos >= nextscene['pos']):
                                out.write("\n\n##SCENE:" + nextscene['name'] + "\n")
                                nextscene = scenenames[file].pop(0) if len(scenenames[file]) > 0 else None
                        # Add the speaker name
                        if speaker:
                            # Usually 7 bytes before there's a 0x10 byte, followed by the speaker expression and then the speaker sprite
                            speakercode = -1
                            f.seek(-7, 1)
                            checkspeaker = f.readByte()
                            if checkspeaker == 0x10:
                                f.seek(1, 1)
                                speakercode = f.readByte()
                            else:
                                # Sometimes, it's 6 bytes before instead so check that one too
                                checkspeaker = f.readByte()
                                if checkspeaker == 0x10:
                                    f.seek(1, 1)
                                    speakercode = f.readByte()
                            if speakercode != -1:
                                if speakercode not in game.speakercodes:
                                    common.logDebug("Unknown speaker code", speakercode)
                                else:
                                    if speakercode != lastspeaker:
                                        out.write("#" + game.speakercodes[speakercode] + "\n")
                                    lastspeaker = speakercode
                        # Read the string
                        f.seek(strpos)
                        readstr = game.readString(f, table)
                        if readstr != "":
                            if readstr[-2:] == ">>":
                                readstr = readstr[:-2]
                            out.write(readstr)
                            out.write("=")
                            if merge and readstr in mergesection:
                                out.write(mergesection[readstr].pop(0))
                                if len(mergesection[readstr]) == 0:
                                    del mergesection[readstr]
                            out.write("\n")
                            common.logDebug("Read string:", readstr)
                    elif opcode in game.repopcodes:
                        while f.readByte() != 0xff:
                            pass
                    else:
                        f.seek(game.opcodes[opcode], 1)
            out.write("\n\n")
        common.logMessage("Done! Extracted", len(files), "files")
