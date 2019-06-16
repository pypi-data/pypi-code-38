import sys
from pathlib import Path
import cutie
import pyautogui as ag
from .util import ctrl_exit
from .. import screen
from ..util import Timer


def get_region_input():
    region = input("region (e.g. 0,0,900,500): ")
    if not region:
        region = None
    else:
        region = tuple([int(i.strip()) for i in region.split(",")][:4])
    return region


def get_filename():
    filename = input("filename: ")
    filename = filename.strip().replace(" ", "_").lower()
    return f"{filename}.png"


def find_image(image_file, region=None):
    timer = Timer()
    timer.start()
    result = screen.locate_image(image_file, region=region)
    timer.stop()
    print(f"   {timer} -> {result}")


def fetch_image_file():
    def list_directory(dirpth):
        dirs = [f for f in dirpth.iterdir() if f.is_dir()]
        files = [
            f
            for f in dirpth.iterdir()
            if f.is_file() and f.suffix.lower() in (".jpg", ".png")
        ]
        dir_pths = [dirpth.parent] + dirs + files

        dir_names = [f"./{f.name}" for f in dirs]
        file_names = [f.name for f in files]
        dir_listing = ["./.."] + dir_names + file_names

        selection = cutie.select(dir_listing, selected_index=0)

        path = dir_pths[selection]

        if path.is_file():
            return path

        return list_directory(path)

    return list_directory(Path.cwd())


@ctrl_exit
def capture():
    response = input("Take screenshot? (Y|N): ")
    if not response.strip().upper() == "Y":
        print("  > no screenshot taken")
        return
    region = get_region_input()
    filename = get_filename()

    img = ag.screenshot(region=region)
    img.save(filename)
    print(f"  > screenshot: {filename}")


@ctrl_exit
def find():
    print("Select image file you want to find:")
    image_file = fetch_image_file()
    if not image_file:
        sys.exit()

    search_area = get_region_input()

    print("Search Whole Screen:")
    find_image(str(image_file))

    print(f"Search Region {search_area}:")
    find_image(str(image_file), region=search_area)
