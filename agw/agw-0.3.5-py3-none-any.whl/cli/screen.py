import sys
from pathlib import Path
import cutie
import pyautogui as ag
from .util import ctrl_exit
from .. import screen
from ..util import Timer


def parse_list_of_integers(text):
    current_number = []
    for c in text:
        if c in "0123456789":
            current_number.append(c)
        else:
            if current_number:
                yield int("".join(current_number))
            current_number = []
    if current_number:
        yield int("".join(current_number))


def get_region_input(example_text):
    region = input(f"region {example_text}: ").strip()
    if not region:
        return None
    return list(parse_list_of_integers(region))


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


def click_location_prior_to_capture():
    if not cutie.prompt_yes_or_no("Click screen location prior to capture?"):
        return

    region = get_region_input("(e.g. 900 500)")
    ag.moveTo(region[0], region[1])
    ag.click()


@ctrl_exit
def capture():
    if not cutie.prompt_yes_or_no("Take screenshot?"):
        print("  > no screenshot taken")
        return

    region = get_region_input("(e.g. 0 0 900 500)")

    filename = get_filename()

    click_spot = click_location_prior_to_capture()

    img = ag.screenshot(region=region)
    img.save(filename)
    print(f"  > screenshot: {filename}")


@ctrl_exit
def find():
    print("Select image file you want to find:")
    image_file = fetch_image_file()
    if not image_file:
        sys.exit()

    search_area = get_region_input("(e.g. 0 0 900 500)")

    click_spot = click_location_prior_to_capture()

    print("Search Whole Screen:")
    find_image(str(image_file))

    print(f"Search Region {search_area}:")
    find_image(str(image_file), region=search_area)
