import os
import click
from hacktools import common, ws

version = "0.5.0"
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
def extract(rom, font, script):
    all = not rom and not font and not script
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


@common.cli.command()
@click.option("--font", is_flag=True, default=False)
@click.option("--script", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
@click.option("--no-rom", is_flag=True, default=False)
def repack(font, script, debug, no_rom):
    all = not font and not script
    if all or font:
        import repack_font
        repack_font.run(data)
    if all or script:
        import repack_script
        repack_script.run(data)
    if debug:
        # https://tcrf.net/Neon_Genesis_Evangelion:_Shito_Ikusei
        with common.Stream(outfolder + "bank_14.bin", "rb+") as f:
            f.seek(0x97)
            f.writeUInt(0x4000cc6e)
    if not no_rom:
        if os.path.isdir(replacefolder):
            common.mergeFolder(replacefolder, outfolder)
        ws.repackRom(romfile, rompatch, outfolder, patchfile)


if __name__ == "__main__":
    click.echo("ShitoTranslation version " + version)
    if not os.path.isdir(data):
        common.logError(data, "folder not found.")
        quit()
    common.cli()
