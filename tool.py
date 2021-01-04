import codecs
import os
import click
from hacktools import common, ws

version = "0.7.1"
data = "ShitoData/"
romfile = data + "shito.ws"
rompatch = data + "shito_patched.ws"
patchfile = data + "patch.xdelta"
infolder = data + "extract/"
outfolder = data + "repack/"
replacefolder = data + "replace/"


@common.cli.command()
@click.option("--rom", is_flag=True, default=False)
@click.option("--font", is_flag=True, default=False)
@click.option("--script", is_flag=True, default=False)
@click.option("--credits", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
def extract(rom, font, script, credits, img):
    all = not rom and not font and not script and not credits and not img
    if all or rom:
        ws.extractRom(romfile, infolder, outfolder)
    if all or font:
        with common.Stream(infolder + "bank_10.bin", "rb") as f:
            ws.extractImage(f, data + "font_output.png", 16 * 4, 16 * 244)
        with common.Stream(data + "table_output.txt", "w") as f:
            columns = ("00", "40", "80", "c0")
            for row in range(244):
                for column in range(4):
                    if row < 0x10:
                        f.write("0")
                    f.write(format(row, "x") + columns[column] + "=\n")
                f.write("\n")
    if all or script:
        import extract_script
        extract_script.run(data)
    if all or credits:
        import extract_credits
        extract_credits.run(data)
    if all or img:
        import extract_img
        extract_img.run(data)


@common.cli.command()
@click.option("--font", is_flag=True, default=False)
@click.option("--script", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
@click.option("--angel", is_flag=True, default=False)
@click.option("--no-rom", is_flag=True, default=False)
def repack(font, script, img, debug, angel, no_rom):
    all = not font and not script and not img
    if all or font:
        import repack_font
        repack_font.run(data)
    if all or script:
        import repack_script
        repack_script.run(data)
    if all or img:
        import repack_img
        repack_img.run(data)
    common.copyFile(infolder + "bank_14.bin", outfolder + "bank_14.bin")
    if debug or angel:
        # https://tcrf.net/Neon_Genesis_Evangelion:_Shito_Ikusei
        with common.Stream(outfolder + "bank_14.bin", "rb+") as f:
            if debug:
                f.seek(0x97)
                f.writeUInt(0x4000cc6e)
            f.seek(0xa6b9)
            f.writeByte(0x0e if not angel else 0x0d)
    if not no_rom:
        if os.path.isdir(replacefolder):
            common.mergeFolder(replacefolder, outfolder)
        ws.repackRom(romfile, rompatch, outfolder, patchfile)


@common.cli.command()
@click.argument("text")
def translate(text):
    with codecs.open(data + "table_input.txt", "r", "utf-8") as tablef:
        table = common.getSection(tablef, "")
    invtable = {}
    for c in table.keys():
        invtable[table[c][0]] = c
    ret = ""
    for c in text:
        ret += invtable[c][-2:] + invtable[c][:2]
    common.logMessage(ret)


if __name__ == "__main__":
    click.echo("ShitoTranslation version " + version)
    if not os.path.isdir(data):
        common.logError(data, "folder not found.")
        quit()
    common.cli()
