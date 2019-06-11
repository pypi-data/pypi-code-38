# -*- coding: utf-8 -*-
from gherkan.flask_api import gherkan_rest
import sys


if __name__ == "__main__":
    print("Setting up Gherkan API via __main__")
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    gherkan_rest.main(args)